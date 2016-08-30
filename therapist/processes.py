class Process(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.description = kwargs.pop('description', None)
        self.config = kwargs

    def __call__(self, **kwargs):
        return self.execute(**kwargs)

    def __str__(self):
        return self.description if self.description else self.name

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)

    def execute(self, **kwargs):
        raise NotImplementedError()  # pragma: nocover
