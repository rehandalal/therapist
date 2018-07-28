import subprocess

from therapist.collection import Collection
from therapist.exc import Error
from therapist.process import Process
from therapist.runner.result import Result


class Action(Process):
    def execute(self, **kwargs):
        files = self.filter_files(kwargs.get('files'))
        should_fix = kwargs.get('fix')

        result = Result(self)

        if should_fix and 'fix' in self.config:
            command = self.config.get('fix')
        else:
            command = self.config.get('run')

        if command and files:
            command_with_args = command.format(files=' '.join(files))

            try:
                pipes = subprocess.Popen(command_with_args, shell=True, cwd=kwargs.get('cwd'), stdout=subprocess.PIPE,
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
