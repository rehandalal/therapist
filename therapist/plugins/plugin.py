from therapist.collection import Collection
from therapist.exc import Error
from therapist.process import Process


class Plugin(Process):  # pragma: no cover
    def __repr__(self):
        return '<Plugin {}>'.format(self.name)

    def execute(self, **kwargs):
        raise NotImplementedError()


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
