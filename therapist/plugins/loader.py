import pkg_resources

from therapist.plugins import Plugin
from therapist.plugins.exc import InvalidPlugin, PluginNotInstalled


def list_plugins():
    return [entry_point.name for entry_point in pkg_resources.iter_entry_points(group='therapist.plugin')]


def load_plugin(name):
    for entry_point in pkg_resources.iter_entry_points(group='therapist.plugin', name=name):
        plugin = entry_point.load()

        if issubclass(plugin, Plugin):
            return plugin
        else:
            raise InvalidPlugin('Plugin must inherit from `Plugin`.')
    raise PluginNotInstalled('Plugin `{}` has not been installed.'.format(name))
