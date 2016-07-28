import os
import stat

from shutil import copy

import click

from therapist import Runner
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
@click.argument('paths', nargs=-1)
@click.option('--action', '-a', default=None, help='A name of a specific action to be run.')
@click.option('--include-unstaged', is_flag=True, help='Include unstaged files.')
@click.option('--include-untracked', is_flag=True, help='Include untracked files.')
def run(paths, action, include_unstaged, include_untracked):
    """Run actions as a batch or individually."""
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
        runner = Runner(os.path.join(repo_root, '.therapist.yml'), files=files, ignore_unstaged_changes=True,
                        include_unstaged=include_unstaged, include_untracked=include_untracked)
    except Runner.Misconfigured as err:
        printer.fprint('Misconfigured: '.format(err.message), 'red')
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

    hookpath = os.path.join(gitdirpath, 'hooks', 'pre-commit')

    if not os.path.isfile(hookpath):
        printer.fprint('There is no hook to uninstall.', 'yellow')
        exit(1)

    if click.confirm('Are you sure you want to uninstall the current pre-commit hook?'):
        printer.fprint('Uninstalling pre-commit hook...', inline=True)
        os.remove(hookpath)
        printer.fprint('\tDONE', 'green', 'bold')
