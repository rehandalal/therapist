import pytest
import re

import six

from therapist import Runner

from . import Project


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
        result = r.run_action('lint')

        assert result.is_failure

        assert project.read('pass.txt') == 'x'

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

    def test_include_untracked(self, project, capsys):
        project.write('fail.txt')

        r = Runner(project.path, include_untracked=True)
        result = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_unstaged(self, project, capsys):
        project.write('fail.txt')

        project.git.add('.')
        project.git.commit(m='Add file.', date='Wed Jul 27 15:13:46 2016 -0400')

        project.write('fail.txt', 'x')

        r = Runner(project.path, include_unstaged=True)
        result = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_unstaged_changes(self, project):
        project.write('pass.txt', 'FAIL')
        project.git.add('.')

        project.write('pass.txt', 'x')

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

        r = Runner(project.path, include_unstaged_changes=True)
        result = r.run_action('lint')
        assert result.is_success

        assert project.read('pass.txt') == 'x'

        out, err = project.git.status(porcelain=True)
        assert 'AM pass.txt' in out

    def test_run_action_does_not_exist(self, project):
        r = Runner(project.path)

        with pytest.raises(r.actions.DoesNotExist):
            r.run_action('notanaction')

    def test_run_action_success(self, project, capsys):
        project.write('pass.py')
        project.git.add('.')

        r = Runner(project.path)
        result = r.run_action('lint')

        assert result.is_success
        assert 'pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_run_action_failure(self, project, capsys):
        project.write('fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        result = r.run_action('lint')
        assert result.is_failure

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_run_action_skipped(self, project, capsys):
        project.write('.ignore.pass.py')
        project.git.add('.')

        r = Runner(project.path)
        r.run_action('lint')

        assert '.ignore.pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SKIPPED]', out)

    def test_run_action_error(self, project, capsys):
        for i in range(1000):
            project.write('pass{}.txt'.format(str(i).ljust(200, '_')))
        project.git.add('.')

        r = Runner(project.path)
        result = r.run_action('lint')
        assert result.is_error

        assert len(r.files) == 1000

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[ERROR!!]', out)

    def test_run_action_skips_deleted(self, project):
        project.write('pass.py')
        project.git.add('.')
        project.git.commit(m='Add file.')
        project.git.rm('pass.py')

        r = Runner(project.path)
        r.run_action('lint')

        assert len(r.files) == 0

    def test_action_no_run(self, tmpdir, capsys):
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
        r.run_action('norun')

        assert 'pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Skips(.+?)\[SKIPPED]', out)

    def test_action_run_issue(self, tmpdir, capsys):
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
        result = r.run_action('runissue')
        assert result.is_failure

        assert 'pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Should fail(.+?)\[FAILURE]', out)

    def test_action_filter_include(self, project, capsys):
        project.write('pass.py')
        project.write('fail.js')
        project.git.add('.')

        r = Runner(project.path)
        r.run_action('lint')

        assert 'fail.js' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_action_filter_exclude(self, project, capsys):
        project.write('pass.py')
        project.write('.ignore.fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        r.run_action('lint')

        assert '.ignore.fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_output_encoded(self, project, capsys):
        project.write('fail.txt')
        project.git.add('.')

        r = Runner(project.path)
        result = r.run_action('lint')

        assert result.is_failure

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert isinstance(out, six.text_type)
        assert 'b"' not in out
        assert "b'" not in out
