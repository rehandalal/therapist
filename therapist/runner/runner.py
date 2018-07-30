import os
import yaml

from therapist.exc import Error
from therapist.plugins.exc import InvalidPlugin, PluginNotInstalled
from therapist.plugins.loader import load_plugin
from therapist.plugins.plugin import PluginCollection
from therapist.runner.action import Action, ActionCollection
from therapist.utils.git import Git, Status


class Runner(object):
    class Misconfigured(Error):
        NO_CONFIG_FILE = 1
        NO_ACTIONS_OR_PLUGINS = 2
        EMPTY_CONFIG = 3
        ACTIONS_WRONGLY_CONFIGURED = 4
        PLUGINS_WRONGLY_CONFIGURED = 5
        PLUGIN_NOT_INSTALLED = 6
        PLUGIN_INVALID = 7

        def __init__(self, *args, **kwargs):
            self.code = kwargs.pop('code', None)
            super(self.__class__, self).__init__(*args, **kwargs)

    def __init__(self, cwd, files=None, include_unstaged=False, include_untracked=False,
                 include_unstaged_changes=False, fix=False, stage_modified_files=False):
        self.actions = ActionCollection()
        self.plugins = PluginCollection()
        self.unstaged_changes = False

        self.cwd = os.path.abspath(cwd)
        self.git = Git(repo_path=self.cwd)
        self.include_unstaged_changes = include_unstaged_changes or include_unstaged
        self.fix = fix
        self.stage_modified_files = stage_modified_files
        self.file_mtimes = {}

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
                        settings = actions[action_name]
                        if settings is None:
                            settings = {}
                        self.actions.append(Action(action_name, **settings))

            if 'plugins' in config:
                try:
                    plugins = config['plugins']
                except TypeError:
                    raise self.Misconfigured('`plugins` was not configured correctly.',
                                             code=self.Misconfigured.PLUGINS_WRONGLY_CONFIGURED)
                else:
                    if not isinstance(plugins, dict):
                        raise self.Misconfigured('`plugins` was not configured correctly.',
                                                 code=self.Misconfigured.PLUGINS_WRONGLY_CONFIGURED)

                    for plugin_name in plugins:
                        try:
                            plugin = load_plugin(plugin_name)
                        except PluginNotInstalled:
                            raise self.Misconfigured('Plugin `{}` is not installed.'.format(plugin_name),
                                                     code=self.Misconfigured.PLUGIN_NOT_INSTALLED)
                        except InvalidPlugin:
                            raise self.Misconfigured('Plugin `{}` is not a valid plugin.'.format(plugin_name),
                                                     code=self.Misconfigured.PLUGIN_INVALID)
                        settings = plugins[plugin_name]
                        if settings is None:
                            settings = {}
                        self.plugins.append(plugin(plugin_name, **settings))

            if not (self.actions or self.plugins):
                raise self.Misconfigured('`actions` or `plugins` must be specified in the configuration file.',
                                         code=self.Misconfigured.NO_ACTIONS_OR_PLUGINS)

        if files is None:
            files = []

            untracked_files = 'all' if include_untracked else 'no'
            out, err, code = self.git.status(porcelain=True, untracked_files=untracked_files)

            for line in out.splitlines():
                file_status = Status(line)

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

        for path in files:
            if os.path.exists(path):
                self.file_mtimes[path] = os.path.getmtime(path)

        self.files = files

    def run_process(self, process):
        """Runs a single action."""
        message = u'#{bright}'
        message += u'{} '.format(str(process)[:68]).ljust(69, '.')

        stashed = False
        if self.unstaged_changes and not self.include_unstaged_changes:
            out, err, code = self.git.stash(keep_index=True, quiet=True)
            stashed = code == 0

        try:
            result = process(files=self.files, cwd=self.cwd, fix=self.fix)

            out, err, code = self.git.status(porcelain=True, untracked_files='no')
            for line in out.splitlines():
                file_status = Status(line)
                if file_status.is_modified:
                    mtime = os.path.getmtime(file_status.path) if os.path.exists(file_status.path) else 0
                    if mtime > self.file_mtimes.get(file_status.path, 0):
                        result.add_modified_file(file_status.path)
                        if self.stage_modified_files:
                            self.git.add(file_status.path)

        except:  # noqa: E722
            raise
        finally:
            if stashed:
                self.git.reset(hard=True, quiet=True)
                self.git.stash.pop(index=True, quiet=True)

        if result.is_success:
            message += u' #{green}[SUCCESS]'
        elif result.is_failure:
            message += u' #{red}[FAILURE]'
        elif result.is_skip:
            message += u' #{cyan}[SKIPPED]'
        elif result.is_error:
            message += u' #{red}[ERROR!!]'

        return result, message
