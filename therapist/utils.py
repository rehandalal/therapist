import re

from fnmatch import translate


def fnmatch_all(name, pats):
    pats = pats if isinstance(pats, list) else [pats]

    match = True
    for pat in pats:
        match &= bool(re.search(translate(pat), name))

    return match


def fnmatch_any(name, pats):
    pats = pats if isinstance(pats, list) else [pats]

    match = False
    for pat in pats:
        match |= bool(re.search(translate(pat), name))

    return match
