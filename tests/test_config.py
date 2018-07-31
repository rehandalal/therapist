import pytest

from therapist.config import Config


class TestConfig(object):
    def test_instantiation(self, project):
        Config(project.path)

    def test_no_config_file(self):
        with pytest.raises(Config.Misconfigured) as err:
            Config('file/that/doesnt/exist')

        assert err.value.code == Config.Misconfigured.NO_CONFIG_FILE

    def test_empty_config_file(self, project):
        project.write('.therapist.yml', '')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.EMPTY_CONFIG

    def test_no_actions_or_plugins_in_config(self, project):
        data = project.get_config_data()
        data.pop('actions')
        data.pop('plugins')
        project.set_config_data(data)

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.NO_ACTIONS_OR_PLUGINS

    def test_actions_wrongly_configured(self, project):
        project.write('.therapist.yml', 'actions')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

        project.write('.therapist.yml', 'actions:\n  flake8')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

    def test_plugins_wrongly_configured(self, project):
        project.write('.therapist.yml', 'plugins')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGINS_WRONGLY_CONFIGURED

        project.write('.therapist.yml', 'plugins:\n  simple')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGINS_WRONGLY_CONFIGURED

    def test_plugin_not_installed(self, project):
        project.write('.therapist.yml', 'plugins:\n  notsimple: ~')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGIN_NOT_INSTALLED

    def test_plugin_invalid(self, project, mock_plugin):
        mock_plugin(plugin_class=Config)

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGIN_INVALID

    def test_shortcuts_wrongly_configured(self, project):
        project.write('.therapist.yml', 'shortcuts')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED

        project.write('.therapist.yml', 'shortcuts:\n  flake8')

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED

    def test_empty_shortcut(self, project):
        project.write('.therapist.yml', 'actions:\n  flake8: ~\nshortcuts:\n  flake8: ~')
        config = Config(project.path)
        assert config.shortcuts[0].name == 'flake8'

    def test_shortcut_option_string(self, project):
        project.write('.therapist.yml', 'actions:\n  flake8: ~\nshortcuts:\n  flake8:\n    options: fix')
        config = Config(project.path)
        assert config.shortcuts[0].name == 'flake8'
        assert config.shortcuts[0].options == {'fix': True}
