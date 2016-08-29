import hashlib
import os
import shutil
import sys

import click
import couleur

from six import print_

from therapist import Runner
from therapist._version import __version__
from therapist.git import Git
from therapist.messages import (NOT_GIT_REPO_MSG, HOOK_ALREADY_INSTALLED_MSG, EXISTING_HOOK_MSG,
                                CONFIRM_PRESERVE_LEGACY_HOOK_MSG, COPYING_HOOK_MSG, DONE_COPYING_HOOK_MSG,
                                CONFIRM_REPLACE_HOOK_MSG, INSTALL_ABORTED_MSG, INSTALLING_HOOK_MSG,
                                DONE_INSTALLING_HOOK_MSG, NO_HOOK_INSTALLED_MSG, UNINSTALL_ABORTED_MSG,
                                CONFIRM_UNINSTALL_HOOK_MSG, CURRENT_HOOK_NOT_THERAPIST_MSG, LEGACY_HOOK_EXISTS_MSG,
                                CONFIRM_RESTORE_LEGACY_HOOK_MSG, COPYING_LEGACY_HOOK_MSG, DONE_COPYING_LEGACY_HOOK_MSG,
                                REMOVING_LEGACY_HOOK_MSG, DONE_REMOVING_LEGACY_HOOK_MSG, UNINSTALLING_HOOK_MSG,
                                DONE_UNINSTALLING_HOOK_MSG, MISCONFIGURED_MSG, UNSTAGED_CHANGES_MSG)
from therapist.runner.results import ResultCollection
from therapist.utils import current_git_dir, identify_hook, list_files


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

git = Git()

couleur.proxy(sys.stdout).enable()


def output(message, **kwargs):
    print_('#{{reset}}{}#{{reset}}'.format(message), **kwargs)


@click.group(invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help='Show the version and exit.')
def cli(version):
    """A smart pre-commit hook for git."""
    if version:
        output('v{}'.format(__version__))


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force installation of the hook. This will replace any existing hook '
                                                  'unless you also use the --preserve-legacy option.')
@click.option('--preserve-legacy', is_flag=True, help='Preserves any existing pre-commit hook.')
def install(force, preserve_legacy):
    """Install the pre-commit hook."""
    git_dir = current_git_dir()

    if git_dir is None:
        output(NOT_GIT_REPO_MSG)
        exit(1)

    with open(os.path.join(BASE_DIR, 'hooks', 'pre-commit-template'), 'r') as f:
        srchook = f.read()
        srchook_hash = hashlib.md5(srchook.encode()).hexdigest()

    dsthook_path = os.path.join(git_dir, 'hooks', 'pre-commit')

    if os.path.isfile(dsthook_path):
        dsthook_hash = identify_hook(dsthook_path)
        if dsthook_hash:
            if dsthook_hash == srchook_hash:
                output(HOOK_ALREADY_INSTALLED_MSG)
                exit(0)
        else:
            if not force and not preserve_legacy:
                print(EXISTING_HOOK_MSG)
                preserve_legacy = click.confirm(CONFIRM_PRESERVE_LEGACY_HOOK_MSG, default=True)

            if preserve_legacy:
                output(COPYING_HOOK_MSG, end='')
                shutil.copy2(dsthook_path, '{}.legacy'.format(dsthook_path))
                output(DONE_COPYING_HOOK_MSG)
            elif not force:
                if not click.confirm(CONFIRM_REPLACE_HOOK_MSG, default=False):
                    output(INSTALL_ABORTED_MSG)
                    exit(1)

    output(INSTALLING_HOOK_MSG, end='')
    with open(dsthook_path, 'w+') as f:
        f.write(srchook.replace('%hash%', srchook_hash))
    os.chmod(dsthook_path, 0o775)
    output(DONE_INSTALLING_HOOK_MSG)


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force uninstallation of the Therapist pre-commit hook. This will '
                                                  'also remove any legacy hook unless you also use the '
                                                  '--restore-legacy option.')
@click.option('--restore-legacy', is_flag=True, help='Restores any legacy pre-commit hook.')
def uninstall(force, restore_legacy):
    """Uninstall the current pre-commit hook."""
    git_dir = current_git_dir()

    if git_dir is None:
        output(NOT_GIT_REPO_MSG)
        exit(1)

    hook_path = os.path.join(git_dir, 'hooks', 'pre-commit')

    if not os.path.isfile(hook_path):
        output(NO_HOOK_INSTALLED_MSG)
        exit(0)

    hook_hash = identify_hook(hook_path)

    if hook_hash:
        if not force:
            if not click.confirm(CONFIRM_UNINSTALL_HOOK_MSG, default=False):
                output(UNINSTALL_ABORTED_MSG)
                exit(1)
    else:
        output(CURRENT_HOOK_NOT_THERAPIST_MSG)
        exit(1)

    legacy_hook_path = os.path.join(git_dir, 'hooks', 'pre-commit.legacy')

    if os.path.isfile(legacy_hook_path):
        if not force and not restore_legacy:
            output(LEGACY_HOOK_EXISTS_MSG)
            restore_legacy = click.confirm(CONFIRM_RESTORE_LEGACY_HOOK_MSG, default=True)
        if restore_legacy:
            output(COPYING_LEGACY_HOOK_MSG, end='')
            shutil.copy2(legacy_hook_path, hook_path)
            os.remove(legacy_hook_path)
            output(DONE_COPYING_LEGACY_HOOK_MSG)
            exit(0)
        else:
            if force or click.confirm('Would you like to remove the legacy hook?', default=False):
                output(REMOVING_LEGACY_HOOK_MSG, end='')
                os.remove(legacy_hook_path)
                output(DONE_REMOVING_LEGACY_HOOK_MSG)

    output(UNINSTALLING_HOOK_MSG, end='')
    os.remove(hook_path)
    output(DONE_UNINSTALLING_HOOK_MSG)


@cli.command()
@click.argument('paths', nargs=-1)
@click.option('--action', '-a', default=None, help='A name of a specific action to be run.')
@click.option('--include-unstaged', is_flag=True, help='Include unstaged files.')
@click.option('--include-unstaged-changes', is_flag=True, help='Include unstaged changes to staged files.')
@click.option('--include-untracked', is_flag=True, help='Include untracked files.')
@click.option('--junit-xml', default=None, help='Create a junit-xml style report file at the given path.')
@click.option('--no-color', is_flag=True, help='Disables colors and other rich output.')
@click.option('--use-tracked-files', is_flag=True, help='Runs actions against all tracked files.')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output, unless an error occurs.')
def run(**kwargs):
    """Run actions as a batch or individually."""
    paths = kwargs.pop('paths', ())
    action = kwargs.pop('action')
    junit_xml = kwargs.pop('junit_xml')
    use_tracked_files = kwargs.pop('use_tracked_files')
    quiet = kwargs.pop('quiet')

    if kwargs.pop('no_color'):
        couleur.proxy(sys.stdout).ignore()

    git_dir = current_git_dir()

    if git_dir is None:
        output(NOT_GIT_REPO_MSG)
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
        output(MISCONFIGURED_MSG.format(err.message))
        exit(1)
    else:
        results = ResultCollection()

        if runner.unstaged_changes and not quiet:
            output(UNSTAGED_CHANGES_MSG, end='\n\n')

        actions = [a.name for a in runner.actions]

        if action:
            actions = [action]

        try:
            for action in actions:
                result, message = runner.run_action(action)
                results.append(result)

                if not quiet:
                    output(message)
        except runner.actions.DoesNotExist as err:
            output('{}\nAvailable actions:'.format(err.message))

            for action in runner.actions:
                output(action.name)

            exit(0)

        if junit_xml:
            with open(junit_xml, 'w+') as f:
                f.write('{}'.format(results.dump_junit()))

        if not quiet:
            output(results.dump())
            output('#{{bold}}{}\nCompleted in: {}s'.format(''.ljust(79, '-'), round(results.execution_time, 2)))

        if results.has_error:
            exit(1)
        elif results.has_failure:
            exit(2)
