# -*- coding: utf-8 -*-

import os
import pytest

from xml.etree import ElementTree as ET

from therapist.config import Config
from therapist.runner import Runner
from therapist.runner.action import Action, ActionCollection
from therapist.runner.result import Result, ResultCollection

from . import Project


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def equivalent_xml(xmlstring, fixture_path):
    eta = ET.fromstring(xmlstring)
    etb = ET.parse(fixture_path)
    xmlsa = ET.tostring(eta, encoding="utf-8", method="xml")
    xmlsb = ET.tostring(etb.getroot(), encoding="utf-8", method="xml")
    return xmlsa == xmlsb


class TestAction(object):
    def test_str(self):
        a = Action("flake8")
        assert str(a) == "flake8"

        a.description = "Flake 8"
        assert str(a) == "Flake 8"

    def test_repr(self):
        a = Action("flake8")
        assert a.__repr__() == "<Action flake8>"

    def test_include(self):
        a = Action("flake8")
        a.include = "*.py"
        assert a.include == ["*.py"]

        a.include = ["a.py", "b.py"]
        assert a.include == ["a.py", "b.py"]

    def test_exclude(self):
        a = Action("flake8")
        a.exclude = "ignore.py"
        assert a.exclude == ["ignore.py"]

        a.exclude = ["a.py", "b.py"]
        assert a.exclude == ["a.py", "b.py"]


class TestActionCollection(object):
    def test_get(self):
        action = Action("flake8")
        actions = ActionCollection([action])

        assert actions.get("flake8") == action

        with pytest.raises(actions.DoesNotExist):
            actions.get("not_an_action")


class TestResult(object):
    def test_str(self):
        a = Action("flake8")

        r = Result(a, status=Result.SUCCESS)
        assert str(r) == "SUCCESS"

        r.status = Result.FAILURE
        assert str(r) == "FAILURE"

        r.status = None
        assert str(r) == "SKIP"

        r.status = Result.ERROR
        assert str(r) == "ERROR"

    def test_action_validation(self):
        with pytest.raises(TypeError):
            Result("something")


class TestResultCollection(object):
    def test_count(self):
        r1 = Result(Action("flake8"), status=Result.SUCCESS)
        r2 = Result(Action("eslint"))
        rs = ResultCollection([r1, r2])
        assert rs.count() == 2
        assert rs.count(status=None) == 1
        assert rs.count(status=Result.FAILURE) == 0

    def test_has_success(self):
        r = Result(Action("flake8"), status=Result.SUCCESS)

        rs = ResultCollection()
        assert not rs.has_success

        rs.append(r)
        assert rs.has_success

    def test_has_failure(self):
        r = Result(Action("flake8"), status=Result.FAILURE)

        rs = ResultCollection()
        assert not rs.has_failure

        rs.append(r)
        assert rs.has_failure

    def test_has_skip(self):
        r = Result(Action("flake8"))

        rs = ResultCollection()
        assert not rs.has_skip

        rs.append(r)
        assert rs.has_skip

    def test_has_error(self):
        r = Result(Action("flake8"), status=Result.ERROR)

        rs = ResultCollection()
        assert not rs.has_error

        rs.append(r)
        assert rs.has_error

    def test_dump_colors(self):
        r = Result(Action("flake8"), status=Result.FAILURE)
        r.mark_complete(output="Failed!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "FAILED: flake8\n"
            "===============================================================================\n"
            "#{reset_all}Failed!\n"
        )

    def test_dump_unicode(self):
        r = Result(Action("flake8"), status=Result.FAILURE)
        r.mark_complete(output="✖")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "FAILED: flake8\n"
            "===============================================================================\n"
            "#{reset_all}✖\n"
        )

    def test_dump_success(self):
        r = Result(Action("flake8"), status=Result.SUCCESS)
        rs = ResultCollection([r])
        assert rs.dump() == ""

    def test_dump_failure(self):
        r = Result(Action("flake8"), status=Result.FAILURE)
        r.mark_complete(output="Failed!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "FAILED: flake8\n"
            "===============================================================================\n"
            "#{reset_all}Failed!\n"
        )

        r = Result(Action("flake8"), status=Result.FAILURE)
        r.mark_complete(error="ERR!", output="Failed!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "FAILED: flake8\n"
            "===============================================================================\n"
            "#{reset_all}Failed!\n"
            "-------------------------------------------------------------------------------\n"
            "Additional error output:\n"
            "-------------------------------------------------------------------------------\n"
            "ERR!\n"
        )

    def test_dump_skip(self):
        r = Result(Action("flake8"))
        rs = ResultCollection([r])
        assert rs.dump() == ""

    def test_dump_error(self):
        r = Result(Action("flake8"), status=Result.ERROR)
        r.mark_complete(output="OH NOES!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "ERROR: flake8\n"
            "===============================================================================\n"
            "#{reset_all}OH NOES!\n"
        )

        r = Result(Action("flake8"), status=Result.ERROR)
        r.mark_complete(error="Yikes!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "ERROR: flake8\n"
            "===============================================================================\n"
            "#{reset_all}Yikes!\n"
        )

        r = Result(Action("flake8"), status=Result.ERROR)
        r.mark_complete(error="ERR!", output="Failed!")
        rs = ResultCollection([r])
        assert rs.dump() == (
            "\n#{red}#{bright}"
            "===============================================================================\n"
            "ERROR: flake8\n"
            "===============================================================================\n"
            "#{reset_all}Failed!\n"
            "-------------------------------------------------------------------------------\n"
            "Additional error output:\n"
            "-------------------------------------------------------------------------------\n"
            "ERR!\n"
        )

    def test_dump_junit_success(self):
        a = Action("flake8", run="flake8 {files}")
        r = Result(a, status=Result.SUCCESS)
        r.end_time = r.start_time + 1
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_success.xml")
        )

    def test_dump_junit_failure(self):
        a = Action("flake8", run="flake8 {files}")
        r = Result(a, status=Result.FAILURE)
        r.mark_complete(output="Failed!")
        r.end_time = r.start_time + 1
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_failure_1.xml")
        )

        r = Result(a, status=Result.FAILURE)
        r.mark_complete(error="ERR!", output="Failed!")
        r.end_time = r.start_time + 1
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_failure_2.xml")
        )

    def test_dump_junit_skip(self):
        a = Action("flake8", run="flake8 {files}")
        r = Result(a)
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_skip.xml")
        )

    def test_dump_junit_error(self):
        a = Action("flake8", run="flake8 {files}")
        r = Result(a, status=Result.ERROR)
        r.mark_complete(output="Error!")
        r.end_time = r.start_time + 1
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_error_1.xml")
        )

        r = Result(a, status=Result.ERROR)
        r.mark_complete(error="ERR!", output="Error!")
        r.end_time = r.start_time + 1
        rs = ResultCollection([r])
        assert equivalent_xml(
            rs.dump_junit(), os.path.join(BASE_DIR, "fixtures/xml/junit_error_2.xml")
        )


class TestRunner(object):
    def test_unstaged_changes(self, project):
        project.write("pass.txt", "FAIL")
        project.git.add(".")

        project.write("pass.txt", "x")

        out, err, code = project.git.status(porcelain=True)
        assert "AM pass.txt" in out

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_failure

        assert project.read("pass.txt") == "x"

        out, err, code = project.git.status(porcelain=True)
        assert "AM pass.txt" in out

    def test_include_untracked(self, project):
        project.write("fail.txt")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True, include_untracked=True)
        result, message = r.run_process(c.actions.get("lint"))
        assert result.is_failure

        assert "fail.txt" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{red}[FAILURE]"
        )

    def test_include_unstaged(self, project):
        project.write("fail.txt")

        project.git.add(".")
        project.git.commit(m="Add file.", date="Wed Jul 27 15:13:46 2016 -0400")

        project.write("fail.txt", "x")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True, include_unstaged=True)
        result, message = r.run_process(c.actions.get("lint"))
        assert result.is_failure

        assert "fail.txt" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{red}[FAILURE]"
        )

    def test_include_unstaged_changes(self, project):
        project.write("pass.txt", "FAIL")
        project.git.add(".")

        project.write("pass.txt", "x")

        out, err, code = project.git.status(porcelain=True)
        assert "AM pass.txt" in out

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True, include_unstaged_changes=True)
        result, message = r.run_process(c.actions.get("lint"))
        assert result.is_success

        assert project.read("pass.txt") == "x"

        out, err, code = project.git.status(porcelain=True)
        assert "AM pass.txt" in out

    def test_run_action_does_not_exist(self, project):
        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)

        with pytest.raises(c.actions.DoesNotExist):
            r.run_process(c.actions.get("notanaction"))

    def test_run_process_success(self, project):
        project.write("pass.py")

        c = Config(project.path)
        r = Runner(c.cwd, files=["pass.py"])
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_success
        assert "pass.py" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{green}[SUCCESS]"
        )

    def test_run_process_failure(self, project):
        project.write("fail.txt")

        c = Config(project.path)
        r = Runner(c.cwd, files=["fail.txt"])
        result, message = r.run_process(c.actions.get("lint"))
        assert result.is_failure

        assert "fail.txt" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{red}[FAILURE]"
        )

    def test_run_process_skipped(self, project):
        project.write(".ignore.pass.py")

        c = Config(project.path)
        r = Runner(c.cwd, files=[".ignore.pass.py"])
        result, message = r.run_process(c.actions.get("lint"))

        assert ".ignore.pass.py" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{cyan}[SKIPPED]"
        )

    def test_run_process_error(self, project):
        for i in range(10000):
            project.write("pass{}.txt".format(str(i).ljust(200, "_")))
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_error
        assert len(r.files) == 10000
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{red}[ERROR!!]"
        )

    def test_run_process_skips_deleted(self, project):
        project.write("pass.py")
        project.git.add(".")
        project.git.commit(m="Add file.")
        project.git.rm("pass.py")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_skip
        assert len(r.files) == 0

    def test_action_no_run(self, tmpdir):
        config_data = {"actions": {"norun": {"description": "Skips"}}}
        project = Project(tmpdir.strpath, config_data=config_data)

        project.write("pass.py")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("norun"))

        assert "pass.py" in r.files
        assert message == (
            "#{bright}Skips ............................................................... "
            "#{cyan}[SKIPPED]"
        )

    def test_action_run_issue(self, tmpdir):
        config_data = {
            "actions": {
                "runissue": {"description": "Should fail", "run": "not-a-real-command {files}"}
            }
        }
        project = Project(tmpdir.strpath, config_data=config_data)

        project.write("pass.py")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("runissue"))
        assert result.is_failure

        assert "pass.py" in r.files
        assert message == (
            "#{bright}Should fail ......................................................... "
            "#{red}[FAILURE]"
        )

    def test_action_filter_include(self, project):
        project.write("pass.py")
        project.write("fail.js")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert "fail.js" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{green}[SUCCESS]"
        )

    def test_action_filter_exclude(self, project):
        project.write("pass.py")
        project.write(".ignore.fail.txt")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert ".ignore.fail.txt" in r.files
        assert message == (
            "#{bright}Linting ............................................................. "
            "#{green}[SUCCESS]"
        )

    def test_unstash_on_error(self, project, monkeypatch):
        project.write("pass.py")
        project.git.add(".")
        project.write("pass.py", "changed")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)

        def raise_exc():
            raise Exception

        monkeypatch.setattr("time.time", raise_exc)

        with pytest.raises(Exception):
            r.run_process(c.actions.get("lint"))

        assert project.read("pass.py") == "changed"

    def test_output_encoded(self, project):
        project.write("fail.txt")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_failure

        assert "fail.txt" in r.files

        assert isinstance(message, str)
        assert 'b"' not in message
        assert "b'" not in message

    def test_run_process_no_settings(self, tmpdir):
        config_data = {"actions": {"no-settings": None}}
        project = Project(tmpdir.strpath, config_data=config_data)

        project.write("pass.py")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("no-settings"))

        assert "pass.py" in r.files
        assert message == (
            "#{bright}no-settings ......................................................... "
            "#{cyan}[SKIPPED]"
        )

    def test_user_stashed_files_are_not_unstashed(self, project):
        project.write("test.txt", "unchanged")
        project.git.add(".")
        project.git.commit(m="first commit")

        project.write("test.txt", "changed")
        project.git.stash()
        out, err, code = project.git.stash.list()

        assert project.read("test.txt") == "unchanged"
        assert out.startswith("stash@{0}")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))
        out, err, code = project.git.stash.list()

        assert result.is_skip
        assert out.startswith("stash@{0}")

    def test_files_are_not_deleted_when_stash_fails(self, tmpdir):
        project = Project(tmpdir.strpath, blank=True)

        config = {"actions": {"lint": {"run": "false"}}}

        project.set_config_data(config, commit=False)

        project.write("fail.txt")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_failure
        assert project.exists("fail.txt")

    def test_action_working_dir(self, project):
        project.makedirs("working")
        project.copy("scripts", "working/scripts")
        project.git.add(".")

        config = {
            "actions": {"lint": {"run": "./scripts/lint.py {files}", "working_dir": "working"}}
        }
        project.set_config_data(config, commit=False)

        project.write("fail.txt")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_failure
        assert project.exists("fail.txt")

    def test_action_files_root(self, project):
        project.copy("scripts", "working/scripts")
        project.git.add(".")

        config = {
            "actions": {"lint": {"run": "./scripts/lint.py {files}", "files_root": "working"}}
        }
        project.set_config_data(config, commit=True)

        project.makedirs("working")
        project.write("working/pass.txt")
        project.write("fail.txt")
        project.git.add(".")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert result.is_success
        assert project.exists("fail.txt")

    def test_skips_staged_file_deleted_in_working_tree_with_include_unstaged(self, project):
        project.write("pass.txt")
        project.git.add("pass.txt")
        project.remove("pass.txt")

        c = Config(project.path)
        r = Runner(c.cwd, enable_git=True, include_unstaged=True)
        result, message = r.run_process(c.actions.get("lint"))

        assert len(r.files) == 0
        assert result.is_skip
        assert not project.exists("pass.txt")
