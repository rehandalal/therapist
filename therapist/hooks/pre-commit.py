#!/usr/bin/env python
import os
import subprocess
import yaml

from distutils.spawn import find_executable

from therapist import Runner
from therapist.git import Status
from therapist.printer import Printer

printer = Printer()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GIT_BINARY = find_executable('git')

# Get a list of the modified tracked files
status = subprocess.check_output([GIT_BINARY, 'status', '--porcelain', '-uno'])

files = []

for line in status.splitlines():
    print line
    file_status = Status.from_string(line)

    if file_status.modified:
        printer.fprint('One or more files have been modified since they were added.', 'red')
        exit(1)

    files.append(os.path.join(BASE_DIR, file_status.path))

if files:
    # Try and load the config file
    try:
        with open(os.path.join(BASE_DIR, 'therapist.yml'), 'r') as config_file:
            config = yaml.safe_load(config_file)
    except IOError:
        printer.fprint('ERROR: Missing configuration file.', 'red', 'bold')
        printer.fprint('You must create a `therapist.yml` file or use the --no-verify option.', 'red', 'bold')
        exit(1)
    else:
        # Change the current directory to the base directory
        os.chdir(BASE_DIR)

        # Run the commands
        runner = Runner(config, files)
        runner.run()
