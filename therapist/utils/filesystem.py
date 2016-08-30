import os


def current_git_dir():
    """Locate the .git directory."""
    path = os.path.abspath(os.curdir)
    while path != '/':
        if os.path.isdir(os.path.join(path, '.git')):
            return os.path.join(path, '.git')
        path = os.path.dirname(path)
    return None


def list_files(path):
    """Recursively collects a list of files at a path."""
    files = []
    if os.path.isdir(path):
        for stats in os.walk(path):
            for f in stats[2]:
                files.append(os.path.join(stats[0], f))
    elif os.path.isfile(path):
        files = [path]
    return files
