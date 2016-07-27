import os
import stat

from shutil import copy

import click

from therapist._version import __version__
from therapist.printer import Printer
from therapist.runner import Runner


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
    """A smart pre-commit hook for git."""
    pass


@cli.command()
def install():
    """Install the pre-commit hook."""
    srchook = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hooks', 'pre-commit.py')
    gitdir_path = find_git_dir()

    if gitdir_path is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    dsthook = os.path.join(gitdir_path, 'hooks', 'pre-commit')

    if os.path.isfile(dsthook):
        printer.fprint('There is an existing pre-commit hook.', 'yellow')

        if not click.confirm('Are you sure you want to overwrite this hook?'):
            printer.fprint('Installation aborted.')
            exit(1)

    printer.fprint('Installing pre-commit hook...', inline=True)
    copy(srchook, dsthook)
    os.chmod(dsthook, MODE_775)
    printer.fprint('\tDONE', 'green', 'bold')


@cli.command()
@click.option('--command', '-c', default=None, help='A name of a specific command to be run.')
@click.option('--include-unstaged', is_flag=True, help='Include unstaged files.')
@click.option('--include-untracked', is_flag=True, help='Include untracked files.')
def run(command, include_unstaged, include_untracked):
    """Run one or all the commands."""
    gitdir_path = find_git_dir()

    if gitdir_path is None:
        printer.fprint('Unable to locate git repo.', 'red')
        exit(1)

    repo_root = os.path.dirname(gitdir_path)
    os.chdir(repo_root)

    runner = Runner(os.path.join(repo_root, '.therapist.yml'), ignore_modified=True, include_unstaged=include_unstaged,
                    include_untracked=include_untracked)

    if command:
        printer.fprint()

        try:
            runner.run_command(command)
        except runner.CommandDoesNotExist:
            printer.fprint('`{}` is not a valid command.'.format(command))
            printer.fprint()
            printer.fprint('Available commands:')

            for c in runner.commands:
                printer.fprint(c)

        printer.fprint()
    else:
        runner.run()


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
