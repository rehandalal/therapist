import hashlib
import os
import shutil
import stat

import click

from therapist import Runner
from therapist._version import __version__
from therapist.printer import Printer


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MODE_775 = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
            stat.S_IROTH | stat.S_IXOTH)

printer = Printer()


def find_git_dir():
    """Locate the .git directory."""
    path = os.path.abspath(os.curdir)
    while path != '/':
        if os.path.isdir(os.path.join(path, '.git')):
            return os.path.join(path, '.git')
        path = os.path.dirname(path)
    return None


def get_hook_hash(path):
    """Verify that the file at path is the therapist hook and return the hash"""
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            if i == 1:
                if line.startswith('# THERAPIST'):
                    parts = line.split()
                    return parts[2]
                break


@click.group(invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help='Show the version and exit.')
def cli(version):
    """A smart pre-commit hook for git."""
    if version:
        printer.fprint('v{}'.format(__version__))


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force installation of the hook. This will replace any existing hook '
                                                  'unless you also use the --preserve-legacy option.')
@click.option('--preserve-legacy', is_flag=True, help='Preserves any existing pre-commit hook.')
def install(force, preserve_legacy):
    """Install the pre-commit hook."""
    gitdir_path = find_git_dir()

    if gitdir_path is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    with open(os.path.join(BASE_DIR, 'hooks', 'pre-commit-template'), 'r') as f:
        srchook = f.read()
        srchook_hash = hashlib.md5(srchook.encode()).hexdigest()

    dsthook_path = os.path.join(gitdir_path, 'hooks', 'pre-commit')

    if os.path.isfile(dsthook_path):
        dsthook_hash = get_hook_hash(dsthook_path)
        if dsthook_hash:
            if dsthook_hash == srchook_hash:
                printer.fprint('The pre-commit hook has already been installed.')
                exit(0)
            else:
                if not force:
                    printer.fprint('You are not using the current version of the pre-commit hook.', 'yellow')

                    if not click.confirm('Would you like to replace this hook with the current version?', default=True):
                        printer.fprint('Installation aborted.')
                        exit(1)
        else:
            if not force and not preserve_legacy:
                printer.fprint('There is an existing pre-commit hook.', 'yellow')
                printer.fprint('Therapist can preserve this legacy hook and run it before the Therapist pre-commit '
                               'hook.')
                preserve_legacy = click.confirm('Would you like to preserve this legacy hook?', default=True)

            if preserve_legacy:
                printer.fprint('Copying `pre-commit` to `pre-commit.legacy`...\t', inline=True)
                shutil.copy2(dsthook_path, '{}.legacy'.format(dsthook_path))
                printer.fprint('DONE', 'green', 'bold')
            elif not force:
                if not click.confirm('Do you want to replace this hook?', default=False):
                    printer.fprint('Installation aborted.')
                    exit(1)

    printer.fprint('Installing pre-commit hook...\t', inline=True)
    with open(dsthook_path, 'w+') as f:
        f.write(srchook.replace('%hash%', srchook_hash))
    os.chmod(dsthook_path, MODE_775)
    printer.fprint('DONE', 'green', 'bold')


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force uninstallation of the Therapist pre-commit hook. This will '
                                                  'also remove any legacy hook unless you also use the '
                                                  '--restore-legacy option.')
@click.option('--restore-legacy', is_flag=True, help='Restores any legacy pre-commit hook.')
def uninstall(force, restore_legacy):
    """Uninstall the current pre-commit hook."""
    gitdirpath = find_git_dir()

    if gitdirpath is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    hook_path = os.path.join(gitdirpath, 'hooks', 'pre-commit')

    if not os.path.isfile(hook_path):
        printer.fprint('There is no pre-commit hook currently installed.')
        exit(0)

    hook_hash = get_hook_hash(hook_path)

    if hook_hash:
        if not force:
            if not click.confirm('Are you sure you want to uninstall the current pre-commit hook?', default=False):
                printer.fprint('Uninstallation aborted.')
                exit(1)
    else:
        printer.fprint('The current pre-commit hook is not the Therapist pre-commit hook.', 'yellow')
        printer.fprint('Uninstallation aborted.')
        exit(1)

    legacy_hook_path = os.path.join(gitdirpath, 'hooks', 'pre-commit.legacy')

    if os.path.isfile(legacy_hook_path):
        if not force and not restore_legacy:
            printer.fprint('There is a legacy pre-commit hook present.', 'yellow')
            restore_legacy = click.confirm('Would you like to restore the legacy hook?', default=True)
        if restore_legacy:
            printer.fprint('Copying `pre-commit.legacy` to `pre-commit`...\t', inline=True)
            shutil.copy2(legacy_hook_path, hook_path)
            os.remove(legacy_hook_path)
            printer.fprint('DONE', 'green', 'bold')
            exit(0)
        else:
            if force or click.confirm('Would you like to remove the legacy hook?', default=False):
                printer.fprint('Removing `pre-commit.legacy`...\t', inline=True)
                os.remove(legacy_hook_path)
                printer.fprint('DONE', 'green', 'bold')

    printer.fprint('Uninstalling pre-commit hook...\t', inline=True)
    os.remove(hook_path)
    printer.fprint('DONE', 'green', 'bold')


@cli.command()
@click.argument('paths', nargs=-1)
@click.option('--action', '-a', default=None, help='A name of a specific action to be run.')
@click.option('--include-unstaged', is_flag=True, help='Include unstaged files.')
@click.option('--include-untracked', is_flag=True, help='Include untracked files.')
@click.option('--ignore-unstaged-changes', is_flag=True, help='Ignore changes to staged files.')
def run(*args, **kwargs):
    """Run actions as a batch or individually."""
    paths = kwargs.pop('paths', ())
    action = kwargs.pop('action')
    gitdir_path = find_git_dir()

    if gitdir_path is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    repo_root = os.path.dirname(gitdir_path)

    # If paths were provided get all the files for each path
    if paths:
        files = []
        for path in paths:
            if os.path.isdir(path):
                for stats in os.walk(path):
                    for f in stats[2]:
                        files.append(os.path.abspath(os.path.join(stats[0], f)))
            else:
                files.append(os.path.abspath(path))
    else:
        files = None

    try:
        runner = Runner(os.path.join(repo_root, '.therapist.yml'), files=files, **kwargs)
    except Runner.Misconfigured as err:
        printer.fprint('Misconfigured: {}'.format(err.message), 'red')
        exit(1)
    except Runner.UnstagedChanges as err:
        printer.fprint(err.message, 'red')
        exit(1)
    else:
        results = []

        if action:
            printer.fprint()
            try:
                results.append(runner.run_action(action))
            except runner.ActionDoesNotExist as err:
                printer.fprint(err.message)
                printer.fprint()
                printer.fprint('Available actions:')

                for a in runner.actions:
                    printer.fprint(a)
            printer.fprint()
        else:
            results = runner.run()

        exitcode = 0
        for result in results:
            if result['status'] in (Runner.FAILURE, Runner.ERROR):
                exitcode = 1
                printer.fprint(''.ljust(79, '='), 'bold')

                status = 'FAILED' if Runner.FAILURE else 'ERROR'
                printer.fprint('{}: {}'.format(status, result['description']), 'bold')

                printer.fprint(''.ljust(79, '='), 'bold')

                printer.fprint(result['output'])

                printer.fprint()

        exit(exitcode)
