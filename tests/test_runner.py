import pytest
import re

from . import Project
from therapist import Runner


class TestRunner(object):
    def test_instantiation(self, tmpdir):
        p = Project(tmpdir.strpath)
        Runner(p.config_file)

    def test_no_config_file(self):
        with pytest.raises(Runner.Misconfigured) as err:
            Runner('file/that/doesnt/exist', files=['test'])

        assert err.value.code == Runner.Misconfigured.NO_CONFIG_FILE

    def test_no_actions_in_config(self, tmpdir):
        p = Project(tmpdir.strpath)
        data = p.get_config_data()
        data.pop('actions')
        p.set_config_data(data)

        with pytest.raises(Runner.Misconfigured) as err:
            Runner(p.config_file)

        assert err.value.code == Runner.Misconfigured.NO_ACTIONS

    def test_run_commands(self, tmpdir):
        config_data = {
            'actions': {
                'touch': {
                    'description': 'Touch some files',
                    'run': 'touch {files}',
                }
            }
        }

        p = Project(tmpdir.strpath, config_data=config_data)

        r = Runner(p.config_file, files=['file1', 'file2'])
        r.run()

        assert p.exists('file1')
        assert p.exists('file2')

    def test_unstaged_changes(self, tmpdir):
        p = Project(tmpdir.strpath)

        p.write('fail')
        p.git.add('.')

        p.write('fail', 'x')

        with pytest.raises(Runner.UnstagedChanges):
            Runner(p.config_file)

    def test_ignore_unstaged_changes(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        p.write('fail')
        p.git.add('.')

        p.write('fail', 'x')

        r = Runner(p.config_file, ignore_unstaged_changes=True)
        with pytest.raises(SystemExit):
            r.run()

        assert 'fail' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_untracked(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail')

        r = Runner(p.config_file, include_untracked=True)
        with pytest.raises(SystemExit):
            r.run()

        assert 'fail' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_unstaged(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail')

        p.git.add('.')
        p.git.commit(m='Add file')

        p.write('fail', 'x')

        r = Runner(p.config_file, include_unstaged=True)
        with pytest.raises(SystemExit):
            r.run()

        assert 'fail' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_run_action_does_not_exist(self, tmpdir):
        p = Project(tmpdir.strpath)

        r = Runner(p.config_file)

        with pytest.raises(r.ActionDoesNotExist):
            r.run_action('notanaction')

    def test_run_action_success(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('pass')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run()

        assert 'pass' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_run_action_failure(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail')
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(SystemExit):
            r.run()

        assert 'fail' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_run_action_skipped(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('pass.ignore')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run()

        assert 'pass.ignore' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SKIPPED]', out)

    def test_run_action_error(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        for i in range(1000):
            p.write('file{}'.format(str(i).ljust(200, '_')))
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(SystemExit):
            r.run()

        assert len(r.files) == 1000

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[ERROR]', out)
