from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


class Process(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.description = kwargs.pop('description', None)

        self._include = None
        self.include = kwargs.pop('include', None)

        self._exclude = None
        self.exclude = kwargs.pop('exclude', None)

        self.config = kwargs

    def __call__(self, **kwargs):
        return self.execute(**kwargs)

    def __str__(self):
        return self.description if self.description else self.name

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)

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

    def filter_files(self, files):
        if self.include:
            spec = PathSpec(map(GitWildMatchPattern, self.include))
            files = list(spec.match_files(files))

        if self.exclude:
            spec = PathSpec(map(GitWildMatchPattern, self.exclude))
            exclude = list(spec.match_files(files))
            files = list(filter(lambda f: f not in exclude, files))

        return files

    def execute(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover
