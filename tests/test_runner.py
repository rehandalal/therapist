import pytest

import six

from therapist import Runner
from therapist.runner.actions import Action, ActionCollection
from therapist.runner.collections import Collection
from therapist.runner.results import Result, ResultCollection

from . import Project


class TestCollection(object):
    def test_str(self):
        items = ['a', 'b', 'c']
        s = Collection(items)
        assert str(s) == str(items)

    def test_repr(self):
        s = Collection()
        assert s.__repr__() == '<Collection>'

    def test_append(self):
        s = Collection()
        assert len(s.objects) == 0

        s.append('item')
        assert len(s.objects) == 1
        assert s[0] == 'item'

    def test_object_class(self):
        class BooleanCollection(Collection):
            class Meta:
                object_class = bool

        s = BooleanCollection([True])

        with pytest.raises(TypeError):
            s.append('True')


class TestAction(object):
    def test_str(self):
        a = Action('flake8')
        assert str(a) == 'flake8'

        a.description = 'Flake 8'
        assert str(a) == 'Flake 8'

    def test_repr(self):
        a = Action('flake8')
        assert a.__repr__() == '<Action flake8>'

    def test_include(self):
        a = Action('flake8')
        a.include = '*.py'
        assert a.include == ['*.py']

        a.include = ['a.py', 'b.py']
        assert a.include == ['a.py', 'b.py']

    def test_exclude(self):
        a = Action('flake8')
        a.exclude = 'ignore.py'
        assert a.exclude == ['ignore.py']

        a.exclude = ['a.py', 'b.py']
        assert a.exclude == ['a.py', 'b.py']


class TestActionCollection(object):
    def test_get(self):
        action = Action('flake8')
        actions = ActionCollection([action])

        assert actions.get('flake8') == action

        with pytest.raises(actions.DoesNotExist):
            actions.get('not_an_action')


class TestResult(object):
    def test_str(self):
        a = Action('flake8')

        r = Result(a, status=Result.SUCCESS)
        assert str(r) == 'SUCCESS'

        r.status = Result.FAILURE
        assert str(r) == 'FAILURE'

        r.status = Result.SKIP
        assert str(r) == 'SKIP'

        r.status = Result.ERROR
        assert str(r) == 'ERROR'

    def test_repr(self):
        a = Action('flake8')
        r = Result(a)
        assert r.__repr__() == '<Result flake8>'

    def test_action_validation(self):
        with pytest.raises(TypeError):
            Result('something')


class TestResultCollection(object):
    def test_count(self):
        r1 = Result(action=Action('flake8'), status=Result.SUCCESS)
        r2 = Result(action=Action('eslint'), status=Result.SKIP)
        rs = ResultCollection([r1, r2])
        assert rs.count() == 2
        assert rs.count(Result.SKIP) == 1
        assert rs.count(Result.FAILURE) == 0

    def test_has_success(self):
        r = Result(action=Action('flake8'), status=Result.SUCCESS)

        rs = ResultCollection()
        assert not rs.has_success

        rs.append(r)
        assert rs.has_success

    def test_has_failure(self):
        r = Result(action=Action('flake8'), status=Result.FAILURE)

        rs = ResultCollection()
        assert not rs.has_failure

        rs.append(r)
        assert rs.has_failure

    def test_has_skip(self):
        r = Result(action=Action('flake8'), status=Result.SKIP)

        rs = ResultCollection()
        assert not rs.has_skip

        rs.append(r)
        assert rs.has_skip

    def test_has_error(self):
        r = Result(action=Action('flake8'), status=Result.ERROR)

        rs = ResultCollection()
        assert not rs.has_error

        rs.append(r)
        assert rs.has_error

    def test_dump_colors(self):
        r = Result(action=Action('flake8'), status=Result.FAILURE, output='Failed!')
        rs = ResultCollection([r])
        assert rs.dump() == (
            '\n#{red}#{bright}'
            '===============================================================================\n'
            'FAILED: flake8\n'
            '===============================================================================\n'
            '#{reset_all}Failed!'
        )

    def test_dump_success(self):
        r = Result(action=Action('flake8'), status=Result.SUCCESS)
        rs = ResultCollection([r])
        assert rs.dump() == ''

    def test_dump_failure(self):
        r = Result(action=Action('flake8'), status=Result.FAILURE, output='Failed!')
        rs = ResultCollection([r])
        assert rs.dump() == (
            '\n#{red}#{bright}'
            '===============================================================================\n'
            'FAILED: flake8\n'
            '===============================================================================\n'
            '#{reset_all}Failed!'
        )

        r = Result(action=Action('flake8'), status=Result.FAILURE, error='ERR!', output='Failed!')
        rs = ResultCollection([r])
        assert rs.dump() == (
            '\n#{red}#{bright}'
            '===============================================================================\n'
            'FAILED: flake8\n'
            '===============================================================================\n'
            '#{reset_all}ERR!'
        )

    def test_dump_skip(self):
        r = Result(action=Action('flake8'), status=Result.SKIP)
        rs = ResultCollection([r])
        assert rs.dump() == ''

    def test_dump_error(self):
        r = Result(action=Action('flake8'), status=Result.ERROR, output='OH NOES!')
        rs = ResultCollection([r])
        assert rs.dump() == (
            '\n#{red}#{bright}'
            '===============================================================================\n'
            'ERROR: flake8\n'
            '===============================================================================\n'
            '#{reset_all}OH NOES!'
        )

        r = Result(action=Action('flake8'), status=Result.ERROR, error='ERR!', output='Failed!')
        rs = ResultCollection([r])
        assert rs.dump() == (
            '\n#{red}#{bright}'
            '===============================================================================\n'
            'ERROR: flake8\n'
            '===============================================================================\n'
            '#{reset_all}ERR!'
        )

    def test_dump_junit_success(self):
        a = Action('flake8', run='flake8 {files}')
        r = Result(action=a, status=Result.SUCCESS, execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="0" failures="0" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="0" failures="0" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0" />'
            '</testsuite>'
            '</testsuites>'
        )

    def test_dump_junit_failure(self):
        a = Action('flake8', run='flake8 {files}')
        r = Result(action=a, status=Result.FAILURE, output='Failed!', execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="0" failures="1" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="0" failures="1" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0">'
            '<failure type="failure">Failed!</failure>'
            '</testcase>'
            '</testsuite>'
            '</testsuites>'
        )

        r = Result(action=a, status=Result.FAILURE, error='ERR!', output='Failed!', execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="0" failures="1" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="0" failures="1" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0">'
            '<failure type="failure">ERR!</failure>'
            '</testcase>'
            '</testsuite>'
            '</testsuites>'
        )

    def test_dump_junit_skip(self):
        a = Action('flake8', run='flake8 {files}')
        r = Result(action=a, status=Result.SKIP, execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="0" failures="0" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="0" failures="0" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0" />'
            '</testsuite>'
            '</testsuites>'
        )

    def test_dump_junit_error(self):
        a = Action('flake8', run='flake8 {files}')
        r = Result(action=a, status=Result.ERROR, output='Error!', execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="1" failures="0" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="1" failures="0" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0">'
            '<error type="error">Error!</error>'
            '</testcase>'
            '</testsuite>'
            '</testsuites>'
        )

        r = Result(action=a, status=Result.ERROR, error='ERR!', output='Error!', execution_time=1.0)
        rs = ResultCollection([r])
        assert rs.dump_junit() == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="1" failures="0" name="therapist" tests="1" time="1.0">'
            '<testsuite errors="1" failures="0" id="flake8" name="flake8" tests="1" time="1.0">'
            '<testcase name="flake8 {files}" time="1.0">'
            '<error type="error">ERR!</error>'
            '</testcase>'
            '</testsuite>'
            '</testsuites>'
        )


class TestRunner(object):
    def test_instantiation(self, project):
        Runner(project.path)

    def test_no_config_file(self):
        with pytest.raises(Runner.Misconfigured) as err:
            Runner('file/that/doesnt/exist', files=['test'])

        assert err.value.code == Runner.Misconfigured.NO_CONFIG_FILE

    def test_empty_config_file(self, project):
        project.write('.therapist.yml', '')

        with pytest.raises(Runner.Misconfigured) as err:
            Runner(project.path)

        assert err.value.code == Runner.Misconfigured.EMPTY_CONFIG

    def test_no_actions_in_config(self, project):
        data = project.get_config_data()
        data.pop('actions')
        project.set_config_data(data)

        with pytest.raises(Runner.Misconfigured) as err:
            Runner(project.path)

        assert err.value.code == Runner.Misconfigured.NO_ACTIONS

    def test_actions_wrongly_configured(self, project):
        project.write('.therapist.yml', 'actions')

        with pytest.raises(Runner.Misconfigured) as err:
            Runner(project.path)

        assert err.value.code == Runner.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

        project.write('.therapist.yml', 'actions:\n  flake8')

        with pytest.raises(Runner.Misconfigured) as err:
            Runner(project.path)

        assert err.value.code == Runner.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

    def test_unstaged_changes(self, project):
        project.write('pass.txt', 'FAIL')
        project.git.add('.')

        project.write('pass.txt', 'x')

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert result.is_failure

        assert project.read('pass.txt') == 'x'

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

    def test_include_untracked(self, project):
        project.write('fail.txt')

        r = Runner(project.path, include_untracked=True)
        result, message = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{red}[FAILURE]')

    def test_include_unstaged(self, project):
        project.write('fail.txt')

        project.git.add('.')
        project.git.commit(m='Add file.', date='Wed Jul 27 15:13:46 2016 -0400')

        project.write('fail.txt', 'x')

        r = Runner(project.path, include_unstaged=True)
        result, message = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{red}[FAILURE]')

    def test_include_unstaged_changes(self, project):
        project.write('pass.txt', 'FAIL')
        project.git.add('.')

        project.write('pass.txt', 'x')

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

        r = Runner(project.path, include_unstaged_changes=True)
        result, message = r.run_action('lint')
        assert result.is_success

        assert project.read('pass.txt') == 'x'

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

    def test_run_action_does_not_exist(self, project):
        r = Runner(project.path)

        with pytest.raises(r.actions.DoesNotExist):
            r.run_action('notanaction')

    def test_run_action_success(self, project):
        project.write('pass.py')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert result.is_success
        assert 'pass.py' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{green}[SUCCESS]')

    def test_run_action_failure(self, project):
        project.write('fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{red}[FAILURE]')

    def test_run_action_skipped(self, project):
        project.write('.ignore.pass.py')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert '.ignore.pass.py' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{cyan}[SKIPPED]')

    def test_run_action_error(self, project):
        for i in range(1000):
            project.write('pass{}.txt'.format(str(i).ljust(200, '_')))
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')
        assert result.is_error

        assert len(r.files) == 1000
        assert message == ('#{bright}Linting ............................................................. '
                           '#{red}[ERROR!!]')

    def test_run_action_skips_deleted(self, project):
        project.write('pass.py')
        project.git.add('.')
        project.git.commit(m='Add file.')
        project.git.rm('pass.py')

        r = Runner(project.path)
        r.run_action('lint')

        assert len(r.files) == 0

    def test_action_no_run(self, tmpdir):
        config_data = {
            'actions': {
                'norun': {
                    'description': 'Skips',
                }
            }
        }
        project = Project(tmpdir.strpath, config_data=config_data)

        project.write('pass.py')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('norun')

        assert 'pass.py' in r.files
        assert message == ('#{bright}Skips ............................................................... '
                           '#{cyan}[SKIPPED]')

    def test_action_run_issue(self, tmpdir):
        config_data = {
            'actions': {
                'runissue': {
                    'description': 'Should fail',
                    'run': 'pythn {files}',
                }
            }
        }
        project = Project(tmpdir.strpath, config_data=config_data)

        project.write('pass.py')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('runissue')
        assert result.is_failure

        assert 'pass.py' in r.files
        assert message == ('#{bright}Should fail ......................................................... '
                           '#{red}[FAILURE]')

    def test_action_filter_include(self, project):
        project.write('pass.py')
        project.write('fail.js')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert 'fail.js' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{green}[SUCCESS]')

    def test_action_filter_exclude(self, project):
        project.write('pass.py')
        project.write('.ignore.fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert '.ignore.fail.txt' in r.files
        assert message == ('#{bright}Linting ............................................................. '
                           '#{green}[SUCCESS]')

    def test_unstash_on_error(self, project, monkeypatch):
        project.write('pass.py')
        project.git.add('.')
        project.write('pass.py', 'changed')

        r = Runner(project.path)

        def raise_exc():
            raise Exception

        monkeypatch.setattr('time.time', raise_exc)

        with pytest.raises(Exception):
            r.run_action('lint')

        assert project.read('pass.py') == 'changed'

    def test_output_encoded(self, project, capsys):
        project.write('fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        result, message = r.run_action('lint')

        assert result.is_failure

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert isinstance(out, six.text_type)
        assert 'b"' not in out
        assert "b'" not in out
