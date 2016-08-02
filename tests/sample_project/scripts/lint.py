#!/usr/bin/env python
import os
import sys


BASE_DIR = os.path.abspath(os.curdir)


def check(file):
    if 'fail' in file:
        print('FAIL!  {}'.format(file))
        exit(1)


for path in sys.argv[1:]:
    path = os.path.join(BASE_DIR, path)
    if os.path.exists(path):
        if os.path.isdir(path):
            for stats in os.walk(path):
                for f in stats[2]:
                    check(os.path.join(stats[0], f))
        else:
            check(path)

print('SUCCESS!')
