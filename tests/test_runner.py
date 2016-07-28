import pytest

from . import Project
from therapist import Runner
from therapist.utils import chdir


class TestRunner(object):
    def test_can_create(self, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            Runner(p.config_file)

    def test_no_config_file(self, tmpdir):
        with pytest.raises(Runner.Misconfigured) as err:
            Runner('file/that/doesnt/exist', files=['test'])

        assert err.value.code == Runner.Misconfigured.NO_CONFIG_FILE

    def test_no_actions_in_config(self, tmpdir):
        p = Project(tmpdir.strpath)
        data = p.get_config_data()
        data.pop('actions')
        p.set_config_data(data)

        with chdir(p.path):
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

        with chdir(p.path):
            r = Runner(p.config_file, files=['file1', 'file2'])
            r.run()

            assert p.exists('file1')
            assert p.exists('file2')
