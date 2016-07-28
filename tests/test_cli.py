import pytest

from click.testing import CliRunner

from therapist import cli
from therapist._version import __version__
from therapist.context_managers import chdir

from . import Project


@pytest.fixture(scope='class')
def cli_runner():
    return CliRunner()


class TestCLI(object):
    def test_cli_works(self, cli_runner):
        result = cli_runner.invoke(cli.cli)
        assert result.exit_code == 0
        assert not result.exception

    def test_cli_with_version_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ['--version'])
        assert not result.exception
        assert result.exit_code == 0
        assert result.output.strip() == 'therapist, version {}'.format(__version__)

    def test_cli_with_help_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ['--help'])
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_install(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            result = cli_runner.invoke(cli.install)
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_reinstall(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)

            result = cli_runner.invoke(cli.install, input='y')
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.install, input='n')
            assert result.exception
            assert result.exit_code == 1

    def test_cli_install_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.install)
        assert result.exception
        assert result.exit_code == 1

    def test_cli_uninstall(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)

            result = cli_runner.invoke(cli.uninstall, input='n')
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.uninstall, input='y')
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.uninstall)
            assert result.exception
            assert result.exit_code == 1

    def test_cli_uninstall_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.uninstall)
            assert result.exception
            assert result.exit_code == 1

    def test_cli_run(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_run_fails(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
        assert result.exception
        assert result.exit_code == 1

    def test_cli_run_action(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'lint'])
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_run_action_fails(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'lint'])
        assert result.exception
        assert result.exit_code == 1

    def test_cli_run_action_invalid(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'notanaction'])
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_run_pass_file(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['*.py'])
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_run_pass_file_fail(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['*.py'])
        assert result.exception
        assert result.exit_code == 1

    def test_cli_run_pass_dir(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('dir/pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['dir'])
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_run_pass_dir_fail(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('dir/fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['dir'])
        assert result.exception
        assert result.exit_code == 1

    def test_cli_include_untracked(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ['--include-untracked'])
            assert result.exception
            assert result.exit_code == 1

    def test_cli_include_unstaged(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')
        p.git.commit(m='Add file.')
        p.write('fail.py', 'x')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ['--include-unstaged'])
            assert result.exception
            assert result.exit_code == 1

    def test_cli_run_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.run)
        assert result.exception
        assert result.exit_code == 1

    def test_cli_run_no_actions_in_config(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        config_data = p.get_config_data()
        config_data.pop('actions')
        p.set_config_data(config_data)

        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.run)
        assert result.exception
        assert result.exit_code == 1
