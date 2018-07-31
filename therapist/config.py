import os
import yaml

from therapist.exc import Error
from therapist.plugins.exc import InvalidPlugin, PluginNotInstalled
from therapist.plugins.loader import load_plugin
from therapist.plugins.plugin import PluginCollection
from therapist.runner.action import Action, ActionCollection
from therapist.runner.shortcut import Shortcut, ShortcutCollection


class Config(object):
    class Misconfigured(Error):
        NO_CONFIG_FILE = 1
        NO_ACTIONS_OR_PLUGINS = 2
        EMPTY_CONFIG = 3
        ACTIONS_WRONGLY_CONFIGURED = 4
        PLUGINS_WRONGLY_CONFIGURED = 5
        PLUGIN_NOT_INSTALLED = 6
        PLUGIN_INVALID = 7
        SHORTCUTS_WRONGLY_CONFIGURED = 6

        def __init__(self, *args, **kwargs):
            self.code = kwargs.pop('code', None)
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, cwd):
        self.cwd = os.path.abspath(cwd)
        self.actions = ActionCollection()
        self.plugins = PluginCollection()
        self.shortcuts = ShortcutCollection()

        # Try and load the config file
        try:
            with open(os.path.join(self.cwd, '.therapist.yml'), 'r') as f:
                config = yaml.safe_load(f)
        except IOError:
            raise self.Misconfigured('Missing configuration file.', code=self.Misconfigured.NO_CONFIG_FILE)
        else:
            if config is None:
                raise self.Misconfigured('Empty configuration file.', code=self.Misconfigured.EMPTY_CONFIG)

            if 'actions' in config:
                try:
                    actions = config['actions']
                except TypeError:
                    raise self.Misconfigured('`actions` was not configured correctly.',
                                             code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(actions, dict):
                        raise self.Misconfigured('`actions` was not configured correctly.',
                                                 code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)

                    for action_name in actions:
                        settings = actions[action_name]
                        if settings is None:
                            settings = {}
                        self.actions.append(Action(action_name, **settings))

            if 'plugins' in config:
                try:
                    plugins = config['plugins']
                except TypeError:
                    raise self.Misconfigured('`plugins` was not configured correctly.',
                                             code=self.Misconfigured.PLUGINS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(plugins, dict):
                        raise self.Misconfigured('`plugins` was not configured correctly.',
                                                 code=self.Misconfigured.PLUGINS_WRONGLY_CONFIGURED)

                    for plugin_name in plugins:
                        try:
                            plugin = load_plugin(plugin_name)
                        except PluginNotInstalled:
                            raise self.Misconfigured('Plugin `{}` is not installed.'.format(plugin_name),
                                                     code=self.Misconfigured.PLUGIN_NOT_INSTALLED)
                        except InvalidPlugin:
                            raise self.Misconfigured('Plugin `{}` is not a valid plugin.'.format(plugin_name),
                                                     code=self.Misconfigured.PLUGIN_INVALID)
                        settings = plugins[plugin_name]
                        if settings is None:
                            settings = {}
                        self.plugins.append(plugin(plugin_name, **settings))

            if 'shortcuts' in config:
                try:
                    shortcuts = config['shortcuts']
                except TypeError:
                    raise self.Misconfigured('`shortcuts` was not configured correctly.',
                                             code=self.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(shortcuts, dict):
                        raise self.Misconfigured('`shortcuts` was not configured correctly.',
                                                 code=self.Misconfigured.SHORTCUTS_WRONGLY_CONFIGURED)

                    for shortcut_name in shortcuts:
                        settings = shortcuts[shortcut_name]
                        if settings is None:
                            settings = {}
                        self.shortcuts.append(Shortcut(shortcut_name, **settings))

            if not (self.actions or self.plugins):
                raise self.Misconfigured('`actions` or `plugins` must be specified in the configuration file.',
                                         code=self.Misconfigured.NO_ACTIONS_OR_PLUGINS)
