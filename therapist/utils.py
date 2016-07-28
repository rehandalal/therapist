import os
import re

from contextlib import contextmanager
from fnmatch import translate


@contextmanager
def chdir(new_dir):
    cwd = os.path.abspath(os.curdir)
    os.chdir(new_dir)
    yield
    os.chdir(cwd)


def fnmatch_any(name, pats):
    pats = pats if isinstance(pats, list) else [pats]

    match = False
    for pat in pats:
        match |= bool(re.search(translate(pat), name))

    return match
