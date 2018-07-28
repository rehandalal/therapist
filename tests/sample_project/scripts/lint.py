#!/usr/bin/env python
import os
import sys


BASE_DIR = os.path.abspath(os.curdir)


def check(f):
    with open(f, 'r') as fp:
        if 'fail' in f or fp.read().upper() == 'FAIL':
            print('FAIL!  {}'.format(f))
            exit(1)


def fix(f):
    with open(f, 'w') as fp:
        fp.write('FIXED')


def do(path, fn):
    path = os.path.join(BASE_DIR, path)
    if os.path.exists(path):
        if os.path.isdir(path):
            for stats in os.walk(path):
                for f in stats[2]:
                    fn(os.path.join(stats[0], f))
        else:
            fn(path)


if '--fix' in sys.argv[1:]:
    for path in sys.argv[1:]:
        do(path, fix)
else:
    for path in sys.argv[1:]:
        do(path, check)

print('SUCCESS!')
