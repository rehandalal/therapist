import os

from contextlib import contextmanager


@contextmanager
def chdir(path):
    cwd = os.path.abspath(os.curdir)
    os.chdir(path)
    yield
    os.chdir(cwd)
