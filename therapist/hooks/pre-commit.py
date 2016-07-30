#!/usr/bin/env python
# THERAPIST {hash}
import os

from therapist import Runner
from therapist.printer import Printer


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
printer = Printer()


try:
    runner = Runner(os.path.join(BASE_DIR, '.therapist.yml'))
except Runner.Misconfigured as err:
    printer.fprint('Misconfigured: '.format(err.message), 'red')
    exit(1)
except Runner.UnstagedChanges as err:
    printer.fprint(err.message, 'red')
    exit(1)

try:
    runner.run()
except runner.ActionFailed:
    exit(1)
