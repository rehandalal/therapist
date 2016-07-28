#!/usr/bin/env python
import os

from therapist import Runner
from therapist.printer import Printer
from therapist.utils import chdir


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with chdir(BASE_DIR):
    try:
        runner = Runner(os.path.join(BASE_DIR, '.therapist.yml'))
    except Runner.Misconfigured as err:
        printer = Printer()
        printer.fprint('Misconfigured: '.format(err.message), 'red')
        exit(1)

    runner.run()
