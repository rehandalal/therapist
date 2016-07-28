import os
import subprocess
import yaml

from distutils.spawn import find_executable

from therapist.git import Status
from therapist.printer import Printer
from therapist.utils import fnmatch_any


printer = Printer()

GIT_BINARY = find_executable('git')


def execute_action(action, files, cwd):
    if 'include' in action:
        files = [f for f in files if fnmatch_any(f, action['include'])]

    if 'exclude' in action:
        files = [f for f in files if not fnmatch_any(f, action['exclude'])]

    if 'run' in action and files:
        file_list = ' '.join(files)
        run_command = action['run'].format(files=file_list)

        try:
            pipes = subprocess.Popen(run_command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as err:
            return 'OSError {}'.format(str(err)), Runner.ERROR

        std_out, std_err = pipes.communicate()

        if len(std_err):
            return std_err, Runner.FAILURE
        else:
            return std_out, Runner.SUCCESS if pipes.returncode == 0 else Runner.FAILURE

    return None, Runner.SKIPPED


class Runner(object):
    SUCCESS = 0
    FAILURE = 1
    SKIPPED = 2
    ERROR = 3

    class ActionDoesNotExist(Exception):
        def __init__(self, message='', *args, **kwargs):
            self.message = message
            super(self.__class__, self).__init__(*args, **kwargs)

    class Misconfigured(Exception):
        NO_CONFIG_FILE = 1
        NO_ACTIONS = 2

        def __init__(self, message='', code=0, *args, **kwargs):
            self.message = message
            self.code = code
            super(self.__class__, self).__init__(*args, **kwargs)

    class UnstagedChanges(Exception):
        def __init__(self, message='', *args, **kwargs):
            self.message = message
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, config_path, files=None, ignore_unstaged_changes=False, include_unstaged=False,
                 include_untracked=False):
        self.cwd = os.path.abspath(os.path.dirname(config_path))

        if files:
            self.files = files
        else:
            self.files = []

            args = [GIT_BINARY, 'status', '--porcelain']

            if not include_untracked:
                args.append('-uno')

            status = subprocess.check_output(args, cwd=self.cwd).decode()

            for line in status.splitlines():
                file_status = Status.from_string(line)

                # Check if staged files were modified since being staged
                if file_status.is_staged and file_status.is_modified and not ignore_unstaged_changes:
                    raise self.UnstagedChanges('There are unstaged changes.')

                # Skip unstaged files if the `unstaged` flag is False
                if not file_status.is_staged and not include_unstaged and not include_untracked:
                    continue

                # Skip deleted files
                if file_status.is_deleted:
                    continue

                self.files.append(file_status.path)

        # Try and load the config file
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                f.close()
        except IOError:
            raise self.Misconfigured('Missing configuration file.', code=self.Misconfigured.NO_CONFIG_FILE)
        else:
            if 'actions' in config:
                self.actions = config['actions']
            else:
                raise self.Misconfigured('`actions` was not specified in the configuration file.',
                                         code=self.Misconfigured.NO_ACTIONS)

    def run_action(self, action_name):
        """Runs a single action."""
        exitcode = 0
        failures = []
        errors = []

        action = self.actions.get(action_name, None)

        if not action:
            raise self.ActionDoesNotExist('`{}` is not a valid action.'.format(action_name))

        description = '%s ' % action.get('description', action_name)[:68]
        printer.fprint(description.ljust(69, '.'), 'bold', inline=True)

        output, status = execute_action(action, self.files, self.cwd)

        if status == self.SUCCESS:
            printer.fprint(' [SUCCESS]', 'green', 'bold')
        elif status == self.FAILURE:
            printer.fprint(' [FAILURE]', 'red', 'bold')
            if output:
                failures.append({'description': description, 'output': output})
            exitcode = 1
        elif status == self.ERROR:
            printer.fprint('..', 'bold', inline=True)
            printer.fprint(' [ERROR]', 'red', 'bold')
            if output:
                errors.append({'description': description, 'output': output})
            exitcode = 1
        else:
            printer.fprint(' [SKIPPED]', 'cyan', 'bold')

        # Iterate through failures if they exist and print output
        def _print_report(title, report):
            printer.fprint()
            printer.fprint(''.ljust(79, '='), 'bold')
            printer.fprint(title[:79], 'bold')
            printer.fprint(''.ljust(79, '='), 'bold')
            printer.fprint(report)

        for failure in failures:
            _print_report('FAILED: ' + failure['description'], failure['output'])

        for error in errors:
            _print_report('ERROR: ' + error['description'], error['output'])

        return exitcode

    def run(self):
        """Runs the set of actions."""
        if self.files:
            exitcode = 0

            printer.fprint()

            # Run each actions
            for name in self.actions:
                exitcode = self.run_action(name)

            printer.fprint()

            if exitcode:
                exit(exitcode)
