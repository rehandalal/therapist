import pytest
from click.testing import CliRunner
from therapist import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert not result.exception


def test_cli_with_option(runner):
    result = runner.invoke(cli.cli, ['--version'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'therapist, version 0.1'
