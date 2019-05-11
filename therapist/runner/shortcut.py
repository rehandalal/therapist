from therapist.collection import Collection
from therapist.exc import Error


class Shortcut(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.extends = kwargs.pop("extends", None)

        self._options = None
        self.options = kwargs.pop("options", None)

        self._flags = None
        self.flags = kwargs.pop("flags", None)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        if value is None:
            self._options = {}
        elif isinstance(value, dict):
            self._options = {}
            for key in value:
                self._options[key.replace("-", "_")] = value[key]
        else:
            self.options = {value.replace("-", "_"): True}

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, value):
        if value is None:
            self._flags = set()
        elif isinstance(value, set):
            self._flags = value
        elif isinstance(value, list):
            self._flags = set(value)
        else:
            self._flags = set([value])

    def extend(self, apply):
        options = {}
        options.update(self.options)
        options.update(apply.options)

        flags = self.flags
        flags = flags.union(apply.flags)

        return Shortcut(apply.name, extends=self.extends, options=options, flags=flags)


class ShortcutCollection(Collection):
    class Meta:
        object_class = Shortcut

    class DoesNotExist(Error):
        pass

    def get(self, name):
        for shortcut in self.objects:
            if shortcut.name == name:
                return shortcut
        raise self.DoesNotExist("`{}` is not a valid shortcut.".format(name))
