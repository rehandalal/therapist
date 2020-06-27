import re

from therapist import cli, __version__
from therapist.utils.hook import read_hook_hash

from . import chdir


class TestCLI(object):
    def test_cli_no_options(self, cli_runner):
        result = cli_runner.invoke(cli.cli)
        assert not result.output
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_with_version_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ["--version"])
        assert not result.exception
        assert result.exit_code == 0
        assert "v{}".format(__version__) in result.output

    def test_cli_with_help_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ["--help"])
        assert "Usage:" in result.output
        assert not result.exception
        assert result.exit_code == 0


class TestInstall(object):
    def test_install(self, cli_runner, project):
        with chdir(project.path):
            result = cli_runner.invoke(cli.install)
        assert "Installing pre-commit hook..." in result.output
        assert not result.exception
        assert result.exit_code == 0
        assert project.exists(".git/hooks/pre-commit")

    def test_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.install)
        assert "Not a git repository (or any of the parent directories)" in result.output
        assert result.exception
        assert result.exit_code == 1

    def test_try_reinstall(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.install)
            assert "The pre-commit hook has already been installed." in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_reinstall_with_fix(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")
            old_hash = project.hash(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.install, ["--fix"])
            assert "The pre-commit hook has already been installed." not in result.output
            assert not result.exception
            assert result.exit_code == 0
            new_hash = project.hash(".git/hooks/pre-commit")
            assert old_hash != new_hash

    def test_update_outdated(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            hook = project.read(".git/hooks/pre-commit")
            hook_hash = read_hook_hash(project.abspath(".git/hooks/pre-commit"))

            project.write(
                ".git/hooks/pre-commit",
                hook.replace("# THERAPIST {}".format(hook_hash), "# THERAPIST hash"),
            )

            result = cli_runner.invoke(cli.install)
            assert "Installing pre-commit hook..." in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = project.read(".git/hooks/pre-commit")
            assert "# THERAPIST {}".format(hook_hash) in hook

    def test_preserve_existing(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit", "")

            result = cli_runner.invoke(cli.install, input="y")
            assert "There is an existing pre-commit hook." in result.output
            assert "Copying `pre-commit` to `pre-commit.legacy`..." in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = project.read(".git/hooks/pre-commit")
            assert "# THERAPIST" in hook

            assert project.exists(".git/hooks/pre-commit.legacy")

    def test_replace_existing(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit", "")

            result = cli_runner.invoke(cli.install, input="n\ny")
            assert "There is an existing pre-commit hook." in result.output
            assert "Copying `pre-commit` to `pre-commit.legacy`..." not in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = project.read(".git/hooks/pre-commit")
            assert "# THERAPIST" in hook

    def test_replace_existing_cancel(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit", "#!usr/bin/env bash\n\nexit 1")

            result = cli_runner.invoke(cli.install, input="n\nn")
            assert "There is an existing pre-commit hook." in result.output
            assert result.exception
            assert result.exit_code == 1

            hook = project.read(".git/hooks/pre-commit")
            assert hook == "#!usr/bin/env bash\n\nexit 1"

    def test_force_option(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit", "# legacy")

            result = cli_runner.invoke(cli.install, ["-f"])
            assert "There is an existing pre-commit hook." not in result.output
            assert "Installing pre-commit hook..." in result.output
            assert not result.exception
            assert result.exit_code == 0

            assert not project.exists(".git/hooks/pre-commit.legacy")

    def test_force_option_preserve_legacy(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit", "# legacy")

            result = cli_runner.invoke(cli.install, ["-f", "--preserve-legacy"])
            assert "There is an existing pre-commit hook." not in result.output
            assert "Copying `pre-commit` to `pre-commit.legacy`..." in result.output
            assert "Installing pre-commit hook..." in result.output
            assert not result.exception
            assert result.exit_code == 0

            assert "# legacy" in project.read(".git/hooks/pre-commit.legacy")

    def test_force_already_installed(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.install, ["-f"])
            assert "The pre-commit hook has already been installed." in result.output
            assert not result.exception
            assert result.exit_code == 0


class TestUninstall(object):
    def test_uninstall(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.uninstall, input="y")
            assert (
                "Are you sure you want to uninstall the current pre-commit hook?" in result.output
            )
            assert not result.exception
            assert result.exit_code == 0

    def test_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.uninstall)
            assert "Not a git repository (or any of the parent directories)" in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_no_hook(self, cli_runner, project):
        with chdir(project.path):
            result = cli_runner.invoke(cli.uninstall)
            assert "There is no pre-commit hook currently installed." in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_cancel(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.uninstall, input="n")
            assert "Uninstallation aborted." in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_non_therapist_hook(self, cli_runner, project):
        with chdir(project.path):
            project.write(".git/hooks/pre-commit")

            result = cli_runner.invoke(cli.uninstall)
            assert (
                "The current pre-commit hook is not the Therapist pre-commit hook." in result.output
            )
            assert result.exception
            assert result.exit_code == 1

    def test_restore_legacy(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert "# THERAPIST" in project.read(".git/hooks/pre-commit")

            project.write(".git/hooks/pre-commit.legacy", "# legacy")

            result = cli_runner.invoke(cli.uninstall, input="y\ny")
            assert "Would you like to restore the legacy hook?" in result.output
            assert "Copying `pre-commit.legacy` to `pre-commit`..." in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert "# legacy" in project.read(".git/hooks/pre-commit")

    def test_remove_legacy(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert "# THERAPIST" in project.read(".git/hooks/pre-commit")

            project.write(".git/hooks/pre-commit.legacy", "# legacy")

            result = cli_runner.invoke(cli.uninstall, input="y\nn\ny")
            assert "Would you like to restore the legacy hook?" in result.output
            assert "Would you like to remove the legacy hook?" in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not project.exists(".git/hooks/pre-commit")
            assert not project.exists(".git/hooks/pre-commit.legacy")

    def test_dont_restore_or_remove_legacy(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert "# THERAPIST" in project.read(".git/hooks/pre-commit")

            project.write(".git/hooks/pre-commit.legacy", "# legacy")

            result = cli_runner.invoke(cli.uninstall, input="y\nn\nn")
            assert "Would you like to restore the legacy hook?" in result.output
            assert "Would you like to remove the legacy hook?" in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not project.exists(".git/hooks/pre-commit")
            assert project.exists(".git/hooks/pre-commit.legacy")

    def test_force_option(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            project.write(".git/hooks/pre-commit.legacy", "# legacy")

            result = cli_runner.invoke(cli.uninstall, ["-f"])
            assert (
                "Are you sure you want to uninstall the current pre-commit hook?"
                not in result.output
            )
            assert "There is a legacy pre-commit hook present." not in result.output
            assert "Copying `pre-commit.legacy` to `pre-commit`..." not in result.output
            assert "Removing `pre-commit.legacy`..." in result.output
            assert "Uninstalling pre-commit hook..." in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not project.exists(".git/hooks/pre-commit")
            assert not project.exists(".git/hooks/pre-commit.legacy")

    def test_force_option_restore_legacy(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            assert project.exists(".git/hooks/pre-commit")

            project.write(".git/hooks/pre-commit.legacy", "# legacy")

            result = cli_runner.invoke(cli.uninstall, ["-f", "--restore-legacy"])
            assert (
                "Are you sure you want to uninstall the current pre-commit hook?"
                not in result.output
            )
            assert "There is a legacy pre-commit hook present." not in result.output
            assert "Copying `pre-commit.legacy` to `pre-commit`..." in result.output
            assert "Removing `pre-commit.legacy`..." not in result.output
            assert "Uninstalling pre-commit hook..." not in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert "# legacy" in project.read(".git/hooks/pre-commit")
            assert not project.exists(".git/hooks/pre-commit.legacy")

    def test_force_option_not_therapist_hook(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            project.write(".git/hooks/pre-commit", "# SOME OTHER HOOK")

            result = cli_runner.invoke(cli.uninstall, ["-f"])
            assert "Uninstallation aborted." in result.output
            assert result.exception
            assert result.exit_code == 1
            assert project.exists(".git/hooks/pre-commit")


class TestRun(object):
    def test_run(self, cli_runner, project):
        project.write("pass.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["pass.py"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_fails(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_action(self, cli_runner, project):
        project.write("pass.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "lint", "pass.py"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_action_with_fix(self, cli_runner, project):
        project.write("pass.py", "UNFIXED")
        project.git.add(".")
        assert project.read("pass.py") == "UNFIXED"

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "lint", "--fix", "pass.py"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert re.search(
                r"Modified files:.+?pass.py.+?<- Linting", result.output, flags=re.DOTALL
            )
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "FIXED"
            assert project.git.status(porcelain=True) == ("AM pass.py\n", "", 0)

    def test_action_with_fix_git_disabled(self, cli_runner, project):
        project.write("pass.py", "UNFIXED")
        project.git.add(".")
        assert project.read("pass.py") == "UNFIXED"

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "lint", "--fix", "--disable-git", "pass.py"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert re.search(
                r"Modified files:.+?pass.py.+?<- Linting", result.output, flags=re.DOTALL
            )
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "FIXED"
            assert project.git.status(porcelain=True) == ("AM pass.py\n", "", 0)

    def test_action_stage_modified_files(self, cli_runner, project):
        project.write("pass.py", "UNFIXED")
        project.git.add(".")
        assert project.read("pass.py") == "UNFIXED"

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "lint", "--fix", "--stage-modified-files"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert re.search(
                r"Modified files:.+?pass.py.+?<- Linting", result.output, flags=re.DOTALL
            )
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "FIXED"
            assert project.git.status(porcelain=True) == ("A  pass.py\n", "", 0)

    def test_action_fails(self, cli_runner, project):
        project.write("fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "lint", "fail.py"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_action_invalid(self, cli_runner, project):
        project.write("fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-a", "notanaction", "fail.py"])
            assert "Available actions:" in result.output
            assert "lint" in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_plugin_not_installed(self, cli_runner, project):
        project.write(".therapist.yml", "plugins:\n  notsimple: ~")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert "Installed plugins:" in result.output
            assert "simple" in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_plugin(self, cli_runner, project):
        project.write("pass.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-p", "simple"])
            assert re.search(r"simple.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_plugin_fails(self, cli_runner, project, mock_plugin):
        project.write("try.py", "PLUGIN: FAIL")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-p", "simple"])
            assert re.search(r"simple.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_plugin_invalid(self, cli_runner, project, mock_plugin):
        project.write("fail.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["-p", "notaplugin"])
            assert "Available plugins:" in result.output
            assert "simple" in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_dir(self, cli_runner, project):
        project.write("dir/pass.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["dir"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_dir_fail(self, cli_runner, project):
        project.write("dir/fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["dir"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_file(self, cli_runner, project):
        project.write("pass.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["pass.py"])
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_file_fail(self, cli_runner, project):
        project.write("fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["fail.py"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_include_untracked(self, cli_runner, project):
        project.write("fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ["--include-untracked"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_include_unstaged(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")
        project.git.commit(m="Add file.")
        project.write("fail.py", "x")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ["--include-unstaged"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_unstaged_changes(self, cli_runner, project):
        project.write("pass.py", "FAIL")
        project.git.add(".")
        project.write("pass.py", "x")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert "You have unstaged changes." in result.output
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2
            assert project.read("pass.py") == "x"

    def test_include_unstaged_changes(self, cli_runner, project):
        project.write("pass.py", "FAIL")
        project.git.add(".")
        project.write("pass.py", "x")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--include-unstaged-changes"])
            assert "You have unstaged changes." in result.output
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "x"

    def test_use_tracked_files(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")
        project.git.commit(m="Add file.")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--use-tracked-files"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_use_tracked_files_include_untracked(self, cli_runner, project):
        project.write("pass.py")
        project.git.add(".")
        project.git.commit(m="Add file.")

        project.write("fail.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--use-tracked-files", "--include-untracked"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2

    def test_no_false_positive_modified_files(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")
        project.git.commit(m="Add file.")
        project.write("fail.py", "CHANGE")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--use-tracked-files"])
            assert result.exit_code == 2
            assert "Modified files" not in result.output

            result = cli_runner.invoke(cli.run, ["foo.py"])
            assert result.exit_code == 0
            assert "Modified files" not in result.output

    def test_misconfigured(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("actions")
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert "Misconfigured:" in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_quiet(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--quiet"])
            assert result.output == ""
            assert result.exception
            assert result.exit_code == 2

    def test_junit_xml(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run, ["--junit-xml=junit.xml"])
            assert re.search(r"Linting.+?\[FAILURE]", result.output)
            assert result.exception
            assert result.exit_code == 2
            assert project.exists("junit.xml")

            junit_xml = project.read("junit.xml")
            assert junit_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_errors(self, cli_runner, project):
        for i in range(1000):
            project.write("pass{}.txt".format(str(i).ljust(200, "_")))
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert re.search(r"Linting.+?\[ERROR!!]", result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_run_without_git_no_config(self, cli_runner, project):
        project.remove(".therapist.yml")
        project.write("pass.py")

        with chdir(project.path):
            result = cli_runner.invoke(cli.run)
            assert "No Therapist configuration file was found." in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_run_with_expired_hook(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            hook = project.read(".git/hooks/pre-commit")
            project.write(
                ".git/hooks/pre-commit",
                re.sub(r"^# THERAPIST(.+?)v[0-9]+?$", "# THERAPIST\1v1", hook, flags=re.MULTILINE),
            )

            result = cli_runner.invoke(cli.run)
            message = (
                "The installed pre-commit hook is incompatible with the current version of "
                "Therapist."
            )
            assert message in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_run_with_expired_hook_no_version(self, cli_runner, project):
        with chdir(project.path):
            cli_runner.invoke(cli.install)
            hook = project.read(".git/hooks/pre-commit")
            project.write(
                ".git/hooks/pre-commit",
                re.sub(r"^# THERAPIST(.+?)v[0-9]+?$", "# THERAPIST\1", hook, flags=re.MULTILINE),
            )

            result = cli_runner.invoke(cli.run)
            message = (
                "The installed pre-commit hook is incompatible with the current version of "
                "Therapist."
            )
            assert message in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_deleted_files_skipped_when_using_tracked_files(self, cli_runner, project):
        with chdir(project.path):
            project.write("test.txt", "testing")
            project.git.add(".")
            project.git.commit(m="Add file")
            project.remove("test.txt")

            result = cli_runner.invoke(
                cli.run, ["--include-unstaged", "--include-untracked", "--use-tracked-files"]
            )
            assert result.exit_code == 0


class TestUse(object):
    def test_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.use, ["lint"])
        assert "No Therapist configuration file was found." in result.output
        assert result.exception
        assert result.exit_code == 1

    def test_use_shortcut(self, cli_runner, project):
        project.write("pass.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.use, ["lint"])
            assert "$ therapist run --action lint --include-untracked" in result.output
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_use_extended_shortcut(self, cli_runner, project):
        project.write("pass.py", "UNFIXED")
        project.git.add(".")
        assert project.read("pass.py") == "UNFIXED"

        with chdir(project.path):
            result = cli_runner.invoke(cli.use, ["fix"])
            assert "$ therapist run --action lint --fix --include-untracked" in result.output
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert re.search(
                r"Modified files:.+?pass.py.+?<- Linting", result.output, flags=re.DOTALL
            )
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "FIXED"
            assert project.git.status(porcelain=True) == ("AM pass.py\n", "", 0)

    def test_extend_extended_shortcut(self, cli_runner, project):
        project.write("pass.py", "UNFIXED")
        project.git.add(".")
        assert project.read("pass.py") == "UNFIXED"

        with chdir(project.path):
            result = cli_runner.invoke(cli.use, ["fix:all"])
            message = "$ therapist run --action lint --fix --include-untracked --use-tracked-files"
            assert message in result.output
            assert re.search(r"Linting.+?\[SUCCESS]", result.output)
            assert re.search(
                r"Modified files:.+?pass.py.+?<- Linting", result.output, flags=re.DOTALL
            )
            assert not result.exception
            assert result.exit_code == 0
            assert project.read("pass.py") == "FIXED"
            assert project.git.status(porcelain=True) == ("AM pass.py\n", "", 0)

    def test_shortcut_invalid(self, cli_runner, project):
        project.write("fail.py")
        project.git.add(".")

        with chdir(project.path):
            result = cli_runner.invoke(cli.use, ["notarealshortcut"])
            assert "Available shortcuts:" in result.output
            assert "lint" in result.output
            assert "fix" in result.output
            assert result.exception
            assert result.exit_code == 1


class TestHook(object):
    def test_action_failure(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install)
        assert project.exists(".git/hooks/pre-commit")

        project.write("fail.py")
        project.git.add(".")

        out, err, code = project.git.commit(m="Should not get committed.")
        assert "FAIL!  {}".format(project.abspath("fail.py")) in err
        assert "Modified files" not in err

        out, err, code = project.git.status(porcelain=True)
        assert "fail.py" in out

    def test_action_success(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install)
        assert project.exists(".git/hooks/pre-commit")

        project.write("pass.py")
        project.git.add(".")

        out, err, code = project.git.commit(m="Add a file.")
        assert "[SUCCESS]" in err
        assert "Modified files" not in err

        out, err, code = project.git.status(porcelain=True)
        assert not out
        assert not err

    def test_legacy_hook(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install)
        assert project.exists(".git/hooks/pre-commit")

        project.write(".git/hooks/pre-commit.legacy", '#!/usr/bin/env bash\necho "LEGACY"')
        project.chmod(".git/hooks/pre-commit.legacy", 0o775)

        project.write("pass.py")
        project.git.add(".")

        out, err, code = project.git.commit(m="Add a file.")
        assert "LEGACY" in err

        out, err, code = project.git.status(porcelain=True)
        assert not out
        assert not err

    def test_legacy_hook_fails(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install)
        assert project.exists(".git/hooks/pre-commit")

        project.write(".git/hooks/pre-commit.legacy", "#!/usr/bin/env bash\nexit 1")
        project.chmod(".git/hooks/pre-commit.legacy", 0o755)

        project.write("pass.py")
        project.git.add(".")

        project.git.commit(m="Add a file.")

        out, err, code = project.git.status(porcelain=True)
        assert "pass.py" in out
        assert not err

    def test_hook_with_fix(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install, ["--fix"])
        assert project.exists(".git/hooks/pre-commit")

        project.write("pass.py", "UNFIXED")
        project.git.add(".")

        out, err, code = project.git.commit(m="Add a file.")
        assert re.search(r"Modified files:.+?pass.py.+?<- Linting", err, flags=re.DOTALL)
        assert "[SUCCESS]" in err

        out, err, code = project.git.status(porcelain=True)
        assert not out
        assert not err
        assert project.read("pass.py") == "FIXED"

    def test_hook_with_fix_without_stage_modified_files(self, cli_runner, project):
        config_data = project.get_config_data()
        config_data.pop("plugins")
        project.set_config_data(config_data)

        with chdir(project.path):
            cli_runner.invoke(cli.install, ["--fix", "--no-stage-modified-files"])
        assert project.exists(".git/hooks/pre-commit")

        project.write("pass.py", "UNFIXED")
        project.git.add(".")

        out, err, code = project.git.commit(m="Add a file.")
        assert re.search(r"Modified files:.+?pass.py.+?<- Linting", err, flags=re.DOTALL)
        assert "[SUCCESS]" in err

        out, err, code = project.git.status(porcelain=True)
        assert out == " M pass.py\n"
        assert not err
        assert project.read("pass.py") == "FIXED"
