import subprocess

from therapist.collection import Collection
from therapist.exc import Error
from therapist.process import Process
from therapist.runner.result import Result


class Action(Process):
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
