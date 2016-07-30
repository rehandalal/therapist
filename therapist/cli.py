import hashlib
import os
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
def cli(version, *args, **kwargs):
    """A smart pre-commit hook for git."""
    if version:
        printer.fprint('v{}'.format(__version__))


@cli.command()
def install():
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
                printer.fprint('You are not using the current version of the pre-commit hook.', 'yellow')

                if not click.confirm('Would you like to replace this hook with the current version?'):
                    printer.fprint('Installation aborted.')
                    exit(1)
        else:
            printer.fprint('There is an existing pre-commit hook.', 'yellow')

            if not click.confirm('Are you sure you want to replace this hook?'):
                printer.fprint('Installation aborted.')
                exit(1)

    printer.fprint('Installing pre-commit hook...\t', inline=True)
    with open(dsthook_path, 'w+') as f:
        f.write(srchook.format(hash=srchook_hash))
    os.chmod(dsthook_path, MODE_775)
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

    try:
        if action:
            printer.fprint()
            try:
                runner.run_action(action)
            except runner.ActionDoesNotExist as err:
                printer.fprint(err.message)
                printer.fprint()
                printer.fprint('Available actions:')

                for a in runner.actions:
                    printer.fprint(a)
            printer.fprint()
        else:
            runner.run()
    except runner.ActionFailed:
        exit(1)


@cli.command()
def uninstall():
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
        if not click.confirm('Are you sure you want to uninstall the current pre-commit hook?'):
            printer.fprint('Uninstallation aborted.')
            exit(1)
    else:
        printer.fprint('The current pre-commit hook is not the Therapist pre-commit hook.', 'yellow')
        printer.fprint('Uninstallation aborted.')
        exit(1)

    printer.fprint('Uninstalling pre-commit hook...\t', inline=True)
    os.remove(hook_path)
    printer.fprint('DONE', 'green', 'bold')
