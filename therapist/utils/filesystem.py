import os


def current_root():
    """Traverse up the tree and locate the first directory with a `.therapist.yml` file."""
    path = os.path.abspath(os.curdir)
    while path:
        if os.path.isfile(os.path.join(path, ".therapist.yml")):
            return path
        next_path = os.path.dirname(path)
        if next_path == path:
            return None
        path = next_path


def current_git_dir():
    """Locate the .git directory."""
    path = os.path.abspath(os.curdir)
    while path:
        if os.path.isdir(os.path.join(path, ".git")):
            return os.path.join(path, ".git")
        next_path = os.path.dirname(path)
        if next_path == path:
            return None
        path = next_path


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
