from therapist.runner.collections import Collection


class Action(object):
    def __init__(self, name, description=None, run=None, include=None, exclude=None):
        self.name = name
        self.description = description
        self.run = run

        self._include = None
        self.include = include

        self._exclude = None
        self.exclude = exclude

    def __str__(self):
        return self.description if self.description else self.name

    def __repr__(self):
        return '<Action {}>'.format(self.name)

    @property
    def include(self):
        return self._include

    @include.setter
    def include(self, value):
        if value is None:
            self._include = []
        else:
            self._include = value if isinstance(value, list) else [value]

    @property
    def exclude(self):
        return self._exclude

    @exclude.setter
    def exclude(self, value):
        if value is None:
            self._exclude = []
        else:
            self._exclude = value if isinstance(value, list) else [value]


class ActionCollection(Collection):
    class Meta:
        object_class = Action

    class DoesNotExist(Exception):
        def __init__(self, message=None, *args, **kwargs):
            self.message = message
            super(self.__class__, self).__init__(*args, **kwargs)

    def get(self, name):
        for action in self.objects:
            if action.name == name:
                return action
        raise self.DoesNotExist('`{}` is not a valid action.'.format(name))
