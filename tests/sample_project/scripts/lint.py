#!/usr/bin/env python
import sys

for path in sys.argv:
    if path.endswith('fail'):
        exit(1)
