import pkg_resources
import pytest

from click.testing import CliRunner

from . import Project, SimplePlugin


@pytest.fixture(scope="class")
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_plugin(monkeypatch):
    def _mock_plugin(name="simple", plugin_class=SimplePlugin):
        class MockedEntryPoint(object):
            def __init__(self):
                self.name = name

            def load(self):
                return plugin_class

        def mock_iter_entry_points(*args, **kwargs):
            ep_name = kwargs.pop("name", name)
            if ep_name == name:
                return [MockedEntryPoint()]
            else:
                return []

        monkeypatch.setattr(pkg_resources, "iter_entry_points", mock_iter_entry_points)

    return _mock_plugin


@pytest.fixture
def project(tmpdir, mock_plugin):
    mock_plugin()
    return Project(tmpdir.strpath)
