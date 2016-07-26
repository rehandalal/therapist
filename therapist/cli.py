import os
import stat

from shutil import copy

import click

from therapist._version import __version__
from therapist.printer import Printer


MODE_775 = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
            stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
            stat.S_IROTH | stat.S_IXOTH)

printer = Printer()


def find_git_dir():
    """Locate the .git directory."""
    path = os.path.abspath(os.curdir)
    while path != os.path.abspath('/'):
        if os.path.isdir(os.path.join(path, '.git')):
            return os.path.join(path, '.git')
        path = os.path.dirname(path)
    return None


@click.group()
@click.version_option(__version__, prog_name='therapist')
def cli():
    """Smart pre-commit hook for git."""
    pass


@cli.command()
def install():
    """Install the pre-commit hook."""
    srchook = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hooks', 'pre-commit.py')
    gitdirpath = find_git_dir()

    if gitdirpath is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    dsthook = os.path.join(gitdirpath, 'hooks', 'pre-commit')

    if os.path.isfile(dsthook):
        printer.fprint('There is an existing pre-commit hook.', 'yellow')

        if not click.confirm('Are you sure you want to overwrite this hook?'):
            printer.fprint('Install aborted.')
            exit(1)

    printer.fprint('Installing pre-commit hook...', inline=True)
    copy(srchook, dsthook)
    os.chmod(dsthook, MODE_775)
    printer.fprint('\tDONE', 'green', 'bold')


@cli.command()
def uninstall():
    """Uninstall the current pre-commit hook."""
    gitdirpath = find_git_dir()

    if gitdirpath is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    hookpath = os.path.join(gitdirpath, 'hooks', 'pre-commit')

    if not os.path.isfile(hookpath):
        printer.fprint('There is no hook to uninstall.', 'yellow')
        exit(1)

    if click.confirm('Are you sure you want to uninstall the current pre-commit hook?'):
        printer.fprint('Uninstalling pre-commit hook...', inline=True)
        os.remove(hookpath)
        printer.fprint('\tDONE', 'green', 'bold')
