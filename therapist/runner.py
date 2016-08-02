import os
import subprocess
import yaml

from pathspec import GitIgnorePattern, PathSpec

from therapist.git import Git, Status
from therapist.printer import Printer

printer = Printer()


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
            return std_err.decode('utf-8'), Runner.FAILURE
        else:
            return std_out.decode('utf-8'), Runner.SUCCESS if pipes.returncode == 0 else Runner.FAILURE

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
        EMPTY_CONFIG = 3
        ACTIONS_WRONGLY_CONFIGURED = 4

        def __init__(self, message='', code=0, *args, **kwargs):
            self.message = message
            self.code = code
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, config_path, files=None, include_unstaged=False, include_untracked=False,
                 include_unstaged_changes=False):
        self.cwd = os.path.abspath(os.path.dirname(config_path))
        self.git = Git(repo_path=self.cwd)
        self.unstaged_changes = False
        self.include_unstaged_changes = include_unstaged_changes or include_unstaged

        # Try and load the config file
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except IOError:
            raise self.Misconfigured('Missing configuration file.', code=self.Misconfigured.NO_CONFIG_FILE)
        else:
            if config is None:
                raise self.Misconfigured('Empty configuration file.', code=self.Misconfigured.EMPTY_CONFIG)

            if 'actions' in config:
                try:
                    self.actions = config['actions']
                except TypeError:
                    raise self.Misconfigured('`actions` was not configured correctly.',
                                             code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(self.actions, dict):
                        raise self.Misconfigured('`actions` was not configured correctly.',
                                                 code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)
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

            out, err = self.git.status(*args, porcelain=True)

            for line in out.splitlines():
                file_status = Status.from_string(line)

                # Check if staged files were modified since being staged
                if file_status.is_staged and file_status.is_modified:
                    self.unstaged_changes = True

                # Skip unstaged files if the `unstaged` flag is False
                if not file_status.is_staged and not include_unstaged and not include_untracked:
                    continue

                # Skip deleted files
                if file_status.is_deleted:
                    continue

                self.files.append(file_status.path)

    def run_action(self, action_name):
        """Runs a single action."""
        action = self.actions.get(action_name, None)

        if not action:
            raise self.ActionDoesNotExist('`{}` is not a valid action.'.format(action_name))

        result = {
            'description': action.get('description', action_name)[:68]
        }

        printer.fprint('{} '.format(result['description']).ljust(69, '.'), 'bold', inline=True)

        if not self.include_unstaged_changes:
            self.git.stash(keep_index=True, quiet=True)

        try:
            result['output'], result['status'] = execute_action(action, self.files, self.cwd)
        except:
            raise
        finally:
            if not self.include_unstaged_changes:
                self.git.reset(hard=True, quiet=True)
                self.git.stash.pop(index=True, quiet=True)

        if result['status'] == self.SUCCESS:
            printer.fprint(' [SUCCESS]', 'green', 'bold')
        elif result['status'] == self.FAILURE:
            printer.fprint(' [FAILURE]', 'red', 'bold')
        elif result['status'] == self.ERROR:
            printer.fprint('..', 'bold', inline=True)
            printer.fprint(' [ERROR]', 'red', 'bold')
        else:
            printer.fprint(' [SKIPPED]', 'cyan', 'bold')

        return result

    def run(self):
        """Runs the set of actions."""
        results = []

        if self.files:
            printer.fprint()

            # Run each actions
            for name in self.actions:
                results.append(self.run_action(name))

            printer.fprint()

        return results
