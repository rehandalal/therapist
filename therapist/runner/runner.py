import os
import subprocess
import time
import yaml

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from therapist.git import Git, Status
from therapist.printer import BOLD, CYAN, fsprint, GREEN, RED
from therapist.runner.actions import Action, ActionCollection
from therapist.runner.results import Result


class Runner(object):
    class Misconfigured(Exception):
        NO_CONFIG_FILE = 1
        NO_ACTIONS = 2
        EMPTY_CONFIG = 3
        ACTIONS_WRONGLY_CONFIGURED = 4

        def __init__(self, message=None, *args, **kwargs):
            self.message = message
            self.code = kwargs.pop('code', 0)
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, cwd, files=None, include_unstaged=False, include_untracked=False,
                 include_unstaged_changes=False, quiet=False):
        self.actions = ActionCollection()
        self.unstaged_changes = False

        self.cwd = os.path.abspath(cwd)
        self.git = Git(repo_path=self.cwd)
        self.include_unstaged_changes = include_unstaged_changes or include_unstaged
        self.quiet = quiet

        # Try and load the config file
        try:
            with open(os.path.join(self.cwd, '.therapist.yml'), 'r') as f:
                config = yaml.safe_load(f)
        except IOError:
            raise self.Misconfigured('Missing configuration file.', code=self.Misconfigured.NO_CONFIG_FILE)
        else:
            if config is None:
                raise self.Misconfigured('Empty configuration file.', code=self.Misconfigured.EMPTY_CONFIG)

            if 'actions' in config:
                try:
                    actions = config['actions']
                except TypeError:
                    raise self.Misconfigured('`actions` was not configured correctly.',
                                             code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(actions, dict):
                        raise self.Misconfigured('`actions` was not configured correctly.',
                                                 code=self.Misconfigured.ACTIONS_WRONGLY_CONFIGURED)

                    for action_name in actions:
                        attrs = actions[action_name]
                        self.actions.append(Action(action_name, **attrs))
            else:
                raise self.Misconfigured('`actions` was not specified in the configuration file.',
                                         code=self.Misconfigured.NO_ACTIONS)

        if files is None:
            files = []

            untracked_files = 'all' if include_untracked else 'no'
            out, err = self.git.status(porcelain=True, untracked_files=untracked_files)

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

                files.append(file_status.path)

        self.files = files

    def _execute_action(self, name):
        """Executes a single action."""
        start_time = time.time()
        action = self.actions.get(name)
        files = self.files

        result = Result(action, status=Result.SKIP)

        if action.include:
            spec = PathSpec(map(GitWildMatchPattern, action.include))
            files = list(spec.match_files(files))

        if action.exclude:
            spec = PathSpec(map(GitWildMatchPattern, action.exclude))
            exclude = list(spec.match_files(files))
            files = list(filter(lambda f: f not in exclude, files))

        if action.run and files:
            file_list = ' '.join(files)
            run_command = action.run.format(files=file_list)

            try:
                pipes = subprocess.Popen(run_command, shell=True, cwd=self.cwd, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            except OSError as err:
                result.error = 'OSError {}'.format(str(err))
                result.status = Result.ERROR
            else:
                std_out, std_err = pipes.communicate()

                result.output = std_out.decode('utf-8')
                result.error = std_err.decode('utf-8')
                result.status = Result.SUCCESS if pipes.returncode == 0 else Result.FAILURE

        result.execution_time = time.time() - start_time
        return result

    def run_action(self, name):
        """Runs a single action."""
        action = self.actions.get(name)

        if not self.quiet:
            description = action.description if action.description else action.name
            fsprint('{} '.format(description[:68]).ljust(69, '.'), (BOLD,), end='')

        if not self.include_unstaged_changes:
            self.git.stash(keep_index=True, quiet=True)

        try:
            result = self._execute_action(name)
        except:
            raise
        finally:
            if not self.include_unstaged_changes:
                self.git.reset(hard=True, quiet=True)
                self.git.stash.pop(index=True, quiet=True)

        if not self.quiet:
            if result.is_success:
                fsprint(' [SUCCESS]', (GREEN, BOLD,))
            elif result.is_failure:
                fsprint(' [FAILURE]', (RED, BOLD,))
            elif result.is_skip:
                fsprint(' [SKIPPED]', (CYAN, BOLD,))
            elif result.is_error:
                fsprint(' [ERROR!!]', (RED, BOLD,))

        return result
