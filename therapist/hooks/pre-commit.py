#!/usr/bin/env python
import os

from therapist import Runner


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(BASE_DIR)

runner = Runner(os.path.join(BASE_DIR, 'therapist.yml'))
runner.run()
