import pkg_resources
import pytest

from click.testing import CliRunner

from . import Project, SimplePlugin


@pytest.fixture(scope='class')
def cli_runner():
    return CliRunner()


@pytest.fixture
def project(tmpdir, monkeypatch):
    class MockedEntryPoint(object):
        def __init__(self):
            self.name = 'simple'

        def load(self):
            return SimplePlugin

    monkeypatch.setattr(pkg_resources, 'iter_entry_points', lambda *args, **kwargs: [MockedEntryPoint()])
    return Project(tmpdir.strpath)
