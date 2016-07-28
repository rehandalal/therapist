import os
import subprocess
import yaml

from distutils.spawn import find_executable
from pathspec import GitIgnorePattern, PathSpec

from therapist.git import Git, Status
from therapist.printer import Printer

printer = Printer()

GIT_BINARY = find_executable('git')


def execute_action(action, files, cwd):
    if 'include' in action:
        rules = action['include'] if isinstance(action['include'], list) else [action['include']]
        spec = PathSpec(map(GitIgnorePattern, rules))
        files = list(spec.match_files(files))

    if 'exclude' in action:
        rules = action['exclude'] if isinstance(action['exclude'], list) else [action['exclude']]
        spec = PathSpec(map(GitIgnorePattern, rules))
        exclude = list(spec.match_files(files))
        files = list(filter(lambda f: f not in exclude, files))

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

    class ActionFailed(Exception):
        def __init__(self, *args, **kwargs):
            self.actions = args
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, config_path, files=None, ignore_unstaged_changes=False, include_unstaged=False,
                 include_untracked=False):
        self.cwd = os.path.abspath(os.path.dirname(config_path))
        self.git = Git(repo_path=self.cwd)

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

        if files:
            self.files = files
        else:
            self.files = []

            args = []

            if not include_untracked:
                args.append('-uno')

            status = self.git.status(*args, porcelain=True)

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

    def run_action(self, action_name):
        """Runs a single action."""
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
            failures.append({'description': description, 'output': output})
        elif status == self.ERROR:
            printer.fprint('..', 'bold', inline=True)
            printer.fprint(' [ERROR]', 'red', 'bold')
            errors.append({'description': description, 'output': output})
        else:
            printer.fprint(' [SKIPPED]', 'cyan', 'bold')

        # Helper function to print reports
        def _print_report(title, report):
            if report:
                printer.fprint()
                printer.fprint(''.ljust(79, '='), 'bold')
                printer.fprint(title[:79], 'bold')
                printer.fprint(''.ljust(79, '='), 'bold')
                printer.fprint(report)

        for failure in failures:
            _print_report('FAILED: ' + failure['description'], failure['output'])

        for error in errors:
            _print_report('ERROR: ' + error['description'], error['output'])

        if failures or errors:
            raise self.ActionFailed(action_name)

    def run(self):
        """Runs the set of actions."""
        if self.files:
            failures = []

            printer.fprint()

            # Run each actions
            for name in self.actions:
                try:
                    self.run_action(name)
                except self.ActionFailed:
                    failures.append(name)

            printer.fprint()

            if failures:
                raise self.ActionFailed(*failures)
