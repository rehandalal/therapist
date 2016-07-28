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

    def test_run_multiple_actions(self, tmpdir):
        config_data = {
            'actions': {
                'touch': {
                    'description': 'Touch some files',
                    'run': 'touch {files}',
                },
                'echo': {
                    'include': 'file1',
                    'run': 'echo "8" > {files}',
                }
            }
        }

        p = Project(tmpdir.strpath, config_data=config_data)

        r = Runner(p.config_file, files=['file1', 'file2'])
        r.run()

        assert p.exists('file1')
        assert p.exists('file2')

        assert p.read('file1') == '8\n'

    def test_run_failure(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        p.write('fail.txt')
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(r.ActionFailed):
            r.run()

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_unstaged_changes(self, tmpdir):
        p = Project(tmpdir.strpath)

        p.write('fail.txt')
        p.git.add('.')

        p.write('fail.txt', 'x')

        with pytest.raises(Runner.UnstagedChanges):
            Runner(p.config_file)

    def test_ignore_unstaged_changes(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        p.write('fail.txt')
        p.git.add('.')

        p.write('fail.txt', 'x')

        r = Runner(p.config_file, ignore_unstaged_changes=True)
        with pytest.raises(r.ActionFailed):
            r.run_action('lint')

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_untracked(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail.txt')

        r = Runner(p.config_file, include_untracked=True)
        with pytest.raises(r.ActionFailed):
            r.run_action('lint')

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_include_unstaged(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail.txt')

        p.git.add('.')
        p.git.commit(m='Add file.', date='Wed Jul 27 15:13:46 2016 -0400')

        p.write('fail.txt', 'x')

        r = Runner(p.config_file, include_unstaged=True)
        with pytest.raises(r.ActionFailed):
            r.run_action('lint')

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_run_action_does_not_exist(self, tmpdir):
        p = Project(tmpdir.strpath)

        r = Runner(p.config_file)

        with pytest.raises(r.ActionDoesNotExist):
            r.run_action('notanaction')

    def test_run_action_success(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run_action('lint')

        assert 'pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_run_action_failure(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('fail.txt')
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(r.ActionFailed):
            r.run_action('lint')

        assert 'fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[FAILURE]', out)

    def test_run_action_skipped(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('.ignore.pass.py')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run_action('lint')

        assert '.ignore.pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SKIPPED]', out)

    def test_run_action_error(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        for i in range(1000):
            p.write('pass{}.txt'.format(str(i).ljust(200, '_')))
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(r.ActionFailed):
            r.run_action('lint')

        assert len(r.files) == 1000

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[ERROR]', out)

    def test_run_action_skips_deleted(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')
        p.git.commit(m='Add file.')
        p.git.rm('pass.py')

        r = Runner(p.config_file)
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
        p = Project(tmpdir.strpath, config_data=config_data)

        p.write('pass.py')
        p.git.add('.')

        r = Runner(p.config_file)
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
        p = Project(tmpdir.strpath, config_data=config_data)

        p.write('pass.py')
        p.git.add('.')

        r = Runner(p.config_file)
        with pytest.raises(r.ActionFailed):
            r.run_action('runissue')

        assert 'pass.py' in r.files

        out, err = capsys.readouterr()

        assert re.search('Should fail(.+?)\[FAILURE]', out)

    def test_action_filter_include(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        p.write('pass.py')
        p.write('fail.js')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run_action('lint')

        assert 'fail.js' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)

    def test_action_filter_exclude(self, tmpdir, capsys):
        p = Project(tmpdir.strpath)

        p.write('pass.py')
        p.write('.ignore.fail.txt')
        p.git.add('.')

        r = Runner(p.config_file)
        r.run_action('lint')

        assert '.ignore.fail.txt' in r.files

        out, err = capsys.readouterr()

        assert re.search('Linting(.+?)\[SUCCESS]', out)
