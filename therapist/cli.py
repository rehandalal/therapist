import hashlib
import os
import shutil

import click

from therapist import Runner
from therapist._version import __version__
from therapist.git import Git
from therapist.printer import fsprint
from therapist.runner.results import ResultSet
from therapist.utils import current_git_dir, identify_hook, list_files


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

NOT_GIT_REPO_MESSAGE = 'Not a git repository (or any of the parent directories)'

git = Git()


@click.group(invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help='Show the version and exit.')
def cli(version):
    """A smart pre-commit hook for git."""
    if version:
        fsprint('v{}'.format(__version__))


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force installation of the hook. This will replace any existing hook '
                                                  'unless you also use the --preserve-legacy option.')
@click.option('--preserve-legacy', is_flag=True, help='Preserves any existing pre-commit hook.')
def install(force, preserve_legacy):
    """Install the pre-commit hook."""
    git_dir = current_git_dir()

    if git_dir is None:
        fsprint(NOT_GIT_REPO_MESSAGE, 'red')
        exit(1)

    with open(os.path.join(BASE_DIR, 'hooks', 'pre-commit-template'), 'r') as f:
        srchook = f.read()
        srchook_hash = hashlib.md5(srchook.encode()).hexdigest()

    dsthook_path = os.path.join(git_dir, 'hooks', 'pre-commit')

    if os.path.isfile(dsthook_path):
        dsthook_hash = identify_hook(dsthook_path)
        if dsthook_hash:
            if dsthook_hash == srchook_hash:
                fsprint('The pre-commit hook has already been installed.')
                exit(0)
        else:
            if not force and not preserve_legacy:
                fsprint('There is an existing pre-commit hook.', 'yellow')
                fsprint('Therapist can preserve this legacy hook and run it before the Therapist pre-commit hook.')
                preserve_legacy = click.confirm('Would you like to preserve this legacy hook?', default=True)

            if preserve_legacy:
                fsprint('Copying `pre-commit` to `pre-commit.legacy`...\t', inline=True)
                shutil.copy2(dsthook_path, '{}.legacy'.format(dsthook_path))
                fsprint('DONE', 'green', 'bold')
            elif not force:
                if not click.confirm('Do you want to replace this hook?', default=False):
                    fsprint('Installation aborted.')
                    exit(1)

    fsprint('Installing pre-commit hook...\t', inline=True)
    with open(dsthook_path, 'w+') as f:
        f.write(srchook.replace('%hash%', srchook_hash))
    os.chmod(dsthook_path, 0o775)
    fsprint('DONE', 'green', 'bold')


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force uninstallation of the Therapist pre-commit hook. This will '
                                                  'also remove any legacy hook unless you also use the '
                                                  '--restore-legacy option.')
@click.option('--restore-legacy', is_flag=True, help='Restores any legacy pre-commit hook.')
def uninstall(force, restore_legacy):
    """Uninstall the current pre-commit hook."""
    git_dir = current_git_dir()

    if git_dir is None:
        fsprint(NOT_GIT_REPO_MESSAGE, 'red')
        exit(1)

    hook_path = os.path.join(git_dir, 'hooks', 'pre-commit')

    if not os.path.isfile(hook_path):
        fsprint('There is no pre-commit hook currently installed.')
        exit(0)

    hook_hash = identify_hook(hook_path)

    if hook_hash:
        if not force:
            if not click.confirm('Are you sure you want to uninstall the current pre-commit hook?', default=False):
                fsprint('Uninstallation aborted.')
                exit(1)
    else:
        fsprint('The current pre-commit hook is not the Therapist pre-commit hook.', 'yellow')
        fsprint('Uninstallation aborted.')
        exit(1)

    legacy_hook_path = os.path.join(git_dir, 'hooks', 'pre-commit.legacy')

    if os.path.isfile(legacy_hook_path):
        if not force and not restore_legacy:
            fsprint('There is a legacy pre-commit hook present.', 'yellow')
            restore_legacy = click.confirm('Would you like to restore the legacy hook?', default=True)
        if restore_legacy:
            fsprint('Copying `pre-commit.legacy` to `pre-commit`...\t', inline=True)
            shutil.copy2(legacy_hook_path, hook_path)
            os.remove(legacy_hook_path)
            fsprint('DONE', 'green', 'bold')
            exit(0)
        else:
            if force or click.confirm('Would you like to remove the legacy hook?', default=False):
                fsprint('Removing `pre-commit.legacy`...\t', inline=True)
                os.remove(legacy_hook_path)
                fsprint('DONE', 'green', 'bold')

    fsprint('Uninstalling pre-commit hook...\t', inline=True)
    os.remove(hook_path)
    fsprint('DONE', 'green', 'bold')


@cli.command()
@click.argument('paths', nargs=-1)
@click.option('--action', '-a', default=None, help='A name of a specific action to be run.')
@click.option('--output-file', default=None, help='Write report to a file.')
@click.option('--output-format', default=None, help='Which format to use for the report.')
@click.option('--include-unstaged', is_flag=True, help='Include unstaged files.')
@click.option('--include-untracked', is_flag=True, help='Include untracked files.')
@click.option('--include-unstaged-changes', is_flag=True, help='Include unstaged changes to staged files.')
@click.option('--use-tracked-files', is_flag=True, help='Runs actions against all tracked files.')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output, unless an error occurs.')
def run(*args, **kwargs):
    """Run actions as a batch or individually."""
    paths = kwargs.pop('paths', ())
    action = kwargs.pop('action')
    output_file = kwargs.pop('output_file')
    output_format = kwargs.pop('output_format')
    use_tracked_files = kwargs.pop('use_tracked_files')
    quiet = kwargs.get('quiet')

    git_dir = current_git_dir()

    if git_dir is None:
        fsprint(NOT_GIT_REPO_MESSAGE, 'red')
        exit(1)

    repo_root = os.path.dirname(git_dir)

    files = []
    if paths:
        # We want to look at files in their current state if paths are passed through
        kwargs['include_unstaged_changes'] = True

        # If paths were provided get all the files for each path
        for path in paths:
            for f in list_files(path):
                f = os.path.relpath(f, repo_root)
                if not f.startswith('..'):  # Don't include files outside the repo root.
                    files.append(f)
    elif use_tracked_files:
        # If the use tracked files flag was passed, get a list of all the tracked files
        out, err = git.ls_files()
        files = out.splitlines()

    if files or paths:
        kwargs['files'] = files

    try:
        runner = Runner(repo_root, **kwargs)
    except Runner.Misconfigured as err:
        fsprint('Misconfigured: {}'.format(err.message), 'red')
        exit(1)
    else:
        results = ResultSet()

        if runner.unstaged_changes and not quiet:
            fsprint('You have unstaged changes.', 'yellow')

        actions = [a.name for a in runner.actions]

        if action:
            actions = [action]

        try:
            for action in actions:
                results.append(runner.run_action(action))
        except runner.actions.DoesNotExist as err:
            fsprint(err.message)
            fsprint('\nAvailable actions:')

            for action in runner.actions:
                fsprint(action.name)

        if output_format == 'junit':
            results_output = results.dump_junit()
        else:
            results_output = results.dump(colors=bool(output_file))

        if output_file:
            with open(output_file, 'w+') as f:
                f.write('{}'.format(results_output))
        elif results_output and not quiet:
                fsprint('\n{}'.format(results_output))

        if not quiet:
            fsprint('\n{}'.format(''.ljust(79, '-')), 'bold')
            fsprint('Completed in: {}s'.format(round(results.execution_time, 2)), 'bold')

        if results.has_error:
            exit(1)
        elif results.has_failure:
            exit(2)
