import os
import subprocess

from therapist.collection import Collection
from therapist.exc import Error
from therapist.process import Process
from therapist.runner.result import Result


class Action(Process):
    def get_working_directory(self, cwd):
        return os.path.join(cwd, self.config.get("working_dir", ""))

    def filter_files(self, files, **kwargs):
        files = super().filter_files(files)

        cwd = kwargs.get("cwd")

        # Filter by files root
        files_root = os.path.abspath(os.path.join(cwd, self.config.get("files_root", "")))
        if files_root:

            def files_root_matches(f):
                return os.path.abspath(os.path.join(cwd, f)).startswith(files_root)

            files = [f for f in files if files_root_matches(f)]

        # Rewrite the file paths relative to the working directory
        working_dir = self.get_working_directory(cwd)
        if working_dir != cwd:
            files = [os.path.relpath(os.path.join(cwd, f), working_dir) for f in files]

        return files

    def execute(self, **kwargs):
        files = self.filter_files(kwargs.get("files"), cwd=kwargs.get("cwd"))
        should_fix = kwargs.get("fix")

        result = Result(self)

        if should_fix and "fix" in self.config:
            command = self.config.get("fix")
        else:
            command = self.config.get("run")

        if command and files:
            command_with_args = command.format(files=" ".join(files))

            try:
                pipes = subprocess.Popen(
                    command_with_args,
                    shell=True,
                    cwd=self.get_working_directory(kwargs.get("cwd")),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except OSError as err:
                result.mark_complete(status=Result.ERROR, error="OSError {}".format(str(err)))
            else:
                std_out, std_err = pipes.communicate()

                status = Result.SUCCESS if pipes.returncode == 0 else Result.FAILURE
                result.mark_complete(
                    status=status, output=std_out.decode("utf-8"), error=std_err.decode("utf-8")
                )

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
        raise self.DoesNotExist("`{}` is not a valid action.".format(name))
