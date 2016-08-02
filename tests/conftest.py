import pytest

from click.testing import CliRunner

from . import Project


@pytest.fixture(scope='class')
def cli_runner():
    return CliRunner()


@pytest.fixture
def project(tmpdir):
    return Project(tmpdir.strpath)
