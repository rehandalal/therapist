import pytest

from click.testing import CliRunner

from therapist import cli
from therapist._version import __version__


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
