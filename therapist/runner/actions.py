import subprocess

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from therapist.collections import Collection
from therapist.exc import Error
from therapist.processes import Process
from therapist.runner.results import Result


class Action(Process):
    def __init__(self, *args, **kwargs):
        self._include = None
        self.include = kwargs.pop('include', None)

        self._exclude = None
        self.exclude = kwargs.pop('exclude', None)

        super(Action, self).__init__(*args, **kwargs)

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
        files = self.filter_files(kwargs.get('files'))

        result = Result(self)

        if 'run' in self.config and files:
            run_command = self.config.get('run').format(files=' '.join(files))

            try:
                pipes = subprocess.Popen(run_command, shell=True, cwd=kwargs.get('cwd'), stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            except OSError as err:
                result.mark_complete(status=Result.ERROR, error='OSError {}'.format(str(err)))
            else:
                std_out, std_err = pipes.communicate()

                status = Result.SUCCESS if pipes.returncode == 0 else Result.FAILURE
                result.mark_complete(status=status, output=std_out.decode('utf-8'), error=std_err.decode('utf-8'))

        return result


class ActionCollection(Collection):
    class Meta:
        object_class = Action

    class DoesNotExist(Error):
        pass

    def get(self, name):
        for action in self.objects:
            if action.name == name:
                return action
        raise self.DoesNotExist('`{}` is not a valid action.'.format(name))
