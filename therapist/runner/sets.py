class Set(object):
    """A generic iterable set of objects."""
    class Meta:
        pass

    def __init__(self, objects=None):
        self._objects = []

        if objects:
            for obj in objects:
                self.append(obj)

    def __iter__(self):
        return iter(self._objects)

    def __str__(self):
        return str(self._objects)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    @property
    def objects(self):
        return self._objects

    def append(self, v):
        object_class = getattr(self.Meta, 'object_class', object)

        if not isinstance(v, object_class):
            raise TypeError('Expected an instance of `{}`.'.format(object_class.__name__))

        self._objects.append(v)
