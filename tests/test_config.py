import pytest

from therapist import __version__
from therapist.config import Config


class TestConfig(object):
    def test_instantiation(self, project):
        Config(project.path)

    def test_no_config_file(self):
        with pytest.raises(Config.Misconfigured) as err:
            Config("file/that/doesnt/exist")

        assert err.value.code == Config.Misconfigured.NO_CONFIG_FILE

    def test_empty_config_file(self, project):
        project.write(".therapist.yml", "")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.EMPTY_CONFIG

    def test_no_actions_or_plugins_in_config(self, project):
        data = project.get_config_data()
        data.pop("actions")
        data.pop("plugins")
        project.set_config_data(data)

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.NO_ACTIONS_OR_PLUGINS

    def test_actions_wrongly_configured(self, project):
        project.write(".therapist.yml", "actions")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

        project.write(".therapist.yml", "actions:\n  flake8")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.ACTIONS_WRONGLY_CONFIGURED

    def test_plugins_wrongly_configured(self, project):
        project.write(".therapist.yml", "plugins")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGINS_WRONGLY_CONFIGURED

        project.write(".therapist.yml", "plugins:\n  simple")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGINS_WRONGLY_CONFIGURED

    def test_plugin_not_installed(self, project):
        project.write(".therapist.yml", "plugins:\n  notsimple: ~")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGIN_NOT_INSTALLED

    def test_plugin_invalid(self, project, mock_plugin):
        mock_plugin(plugin_class=Config)

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.PLUGIN_INVALID

    def test_shortcuts_wrongly_configured(self, project):
        project.write(".therapist.yml", "shortcuts")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED

        project.write(".therapist.yml", "shortcuts:\n  flake8")

        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)

        assert err.value.code == Config.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED

    def test_empty_shortcut(self, project):
        project.write(".therapist.yml", "actions:\n  flake8: ~\nshortcuts:\n  flake8: ~")
        config = Config(project.path)
        assert config.shortcuts[0].name == "flake8"

    def test_shortcut_option_string(self, project):
        project.write(
            ".therapist.yml", "actions:\n  flake8: ~\nshortcuts:\n  flake8:\n    options: fix"
        )
        config = Config(project.path)
        assert config.shortcuts[0].name == "flake8"
        assert config.shortcuts[0].options == {"fix": True}

    def test_requires_string(self, project):
        project.append(".therapist.yml", "requires: 0.1.1")
        config = Config(project.path)
        assert config.requires.get("min") == "0.1.1"
        assert "max" not in config.requires

    def test_requires_float(self, project):
        project.append(".therapist.yml", "requires: 0.1")
        config = Config(project.path)
        assert config.requires.get("min") == 0.1
        assert "max" not in config.requires

    def test_requires_int(self, project):
        project.append(".therapist.yml", "requires: 1")
        config = Config(project.path)
        assert config.requires.get("min") == 1
        assert "max" not in config.requires

    def test_requires_dict_min_only(self, project):
        project.append(".therapist.yml", "requires: \n  min: 0.1.1")
        config = Config(project.path)
        assert config.requires.get("min") == "0.1.1"
        assert "max" not in config.requires

    def test_requires_dict_max_only(self, project):
        project.append(".therapist.yml", "requires: \n  max: 999")
        config = Config(project.path)
        assert config.requires.get("max") == 999
        assert "min" not in config.requires

    def test_requires_dict_min_max(self, project):
        project.append(".therapist.yml", "requires: \n  min: 0.1.1\n  max: 999")
        config = Config(project.path)
        assert config.requires.get("min") == "0.1.1"
        assert config.requires.get("max") == 999

    def test_requires_dict_min_gt_max(self, project):
        project.append(".therapist.yml", "requires: \n  min: 999\n  max: 0.1.1")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.REQUIRES_WRONGLY_CONFIGURED

    def test_requires_list_wrongly_configured(self, project):
        project.append(".therapist.yml", "requires: \n  - 999\n  - 0.1.1")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.REQUIRES_WRONGLY_CONFIGURED

    def test_requires_dict_wrongly_configured(self, project):
        project.append(".therapist.yml", "requires: \n  min: a\n  max: 0.1.1")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.REQUIRES_WRONGLY_CONFIGURED

    def test_requires_string_wrongly_configured(self, project):
        project.append(".therapist.yml", "requires: a")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.REQUIRES_WRONGLY_CONFIGURED

    def test_requires_mismatch_min(self, project):
        project.append(".therapist.yml", "requires: \n  min: 999")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.VERSION_MISMATCH
        assert err.value.message == "You require Therapist >= 999.0.0."

    def test_requires_mismatch_max(self, project):
        project.append(".therapist.yml", "requires: \n  max: 0.0.1")
        with pytest.raises(Config.Misconfigured) as err:
            Config(project.path)
        assert err.value.code == Config.Misconfigured.VERSION_MISMATCH
        assert err.value.message == "You require Therapist <= 0.0.1."

    def test_requires_equal_version(self, project):
        project.append(".therapist.yml", "requires: {}".format(__version__))
        config = Config(project.path)
        assert config.requires.get("min") == __version__
