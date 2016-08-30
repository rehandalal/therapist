from therapist.collections import Collection
from therapist.exc import Error
from therapist.processes import Process


class Plugin(Process):
    def __repr__(self):
        return '<Plugin {}>'.format(self.name)

    def execute(self, **kwargs):
        raise NotImplementedError()  # pragma: nocover


class PluginCollection(Collection):
    class Meta:
        object_class = Plugin

    class DoesNotExist(Error):
        pass

    def get(self, name):
        for plugin in self.objects:
            if plugin.name == name:
                return plugin
        raise self.DoesNotExist('`{}` is not a valid plugin.'.format(name))
