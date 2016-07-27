import subprocess
import yaml

from distutils.spawn import find_executable

from therapist.git import Status
from therapist.printer import Printer
from therapist.utils import fnmatch_any


printer = Printer()

GIT_BINARY = find_executable('git')


def execute_action(action, files):
    if 'include' in action:
        files = [f for f in files if fnmatch_any(f, action['include'])]

    if 'exclude' in action:
        files = [f for f in files if not fnmatch_any(f, action['exclude'])]

    if 'run' in action and files:
        file_list = ' '.join(files)
        run_command = action['run'].format(files=file_list)

        pipes = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()

        if len(std_err):
            return std_err, Runner.FAILURE
        else:
            return std_out, Runner.SUCCESS if pipes.returncode == 0 else Runner.FAILURE

    return None, Runner.SKIPPED


class Runner(object):
    commands = {}
    files = []

    SUCCESS = 0
    FAILURE = 1
    SKIPPED = 2

    class ActionDoesNotExist(Exception):
        def __init__(self, message, *args, **kwargs):
            self.message = message
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, config_path, ignore_modified=False, include_unstaged=False, include_untracked=False):
        args = [GIT_BINARY, 'status', '--porcelain']

        if not include_untracked:
            args.append('-uno')

        status = subprocess.check_output(args)

        for line in status.splitlines():
            file_status = Status.from_string(line)

            # Check if staged files were modified since being staged
            if file_status.is_staged and file_status.is_modified and not ignore_modified:
                printer.fprint('One or more files have been modified since they were staged.', 'red')
                exit(1)

            # Skip unstaged files if the `unstaged` flag is False
            if not file_status.is_staged and not include_unstaged:
                continue

            # Skip deleted files
            if file_status.is_deleted:
                continue

            self.files.append(file_status.path)

        if self.files:
            # Try and load the config file
            try:
                with open(config_path, 'r') as config_file:
                    config = yaml.safe_load(config_file)
            except IOError:
                printer.fprint('ERROR: Missing configuration file.', 'red', 'bold')
                printer.fprint('You must create a `.therapist.yml` file or use the --no-verify option.', 'red', 'bold')
                exit(1)
            else:
                if 'actions' in config:
                    self.actions = config['actions']
                else:
                    printer.fprint('ERROR: `actions` is missing from configuration file.', 'red', 'bold')
                    exit(1)

    def run_action(self, action_name):
        """Runs a single action."""
        exitcode = 0
        failures = []

        action = self.actions.get(action_name, None)

        if not action:
            raise self.ActionDoesNotExist('`{}` is not a valid action.'.format(action_name))

        description = '%s ' % action.get('description', action_name)[:68]
        printer.fprint(description.ljust(69, '.'), 'bold', inline=True)

        output, status = execute_action(action, self.files)

        if status == self.SUCCESS:
            printer.fprint(' [SUCCESS]', 'green', 'bold')
        elif status == self.FAILURE:
            printer.fprint(' [FAILURE]', 'red', 'bold')
            failures.append({'description': description, 'output': output})
            exitcode = 1
        else:
            printer.fprint(' [SKIPPED]', 'cyan', 'bold')

        # Iterate through failures if they exist and print output
        if failures:
            for failure in failures:
                if failure['output']:
                    printer.fprint()
                    printer.fprint(''.ljust(79, '='), 'bold')
                    printer.fprint('FAILED: ' + failure['description'], 'bold')
                    printer.fprint(''.ljust(79, '='), 'bold')
                    printer.fprint(failure['output'].decode())

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
            exit(exitcode)
