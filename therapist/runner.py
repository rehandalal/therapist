import subprocess

from therapist.printer import Printer


printer = Printer()


def execute_command(command):
    """Executes a therapist command."""
    if 'run' in command:
        pipes = subprocess.Popen(command.get('run'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()

        if len(std_err):
            return std_err, Runner.FAILURE
        else:
            status = Runner.SUCCESS if pipes.returncode == 0 else Runner.FAILURE
            return std_out, status
    else:
        return None, Runner.SKIPPED


class Runner(object):
    SUCCESS = 0
    FAILURE = 1
    SKIPPED = 2

    def __init__(self, commands):
        self.commands = commands

    def run(self):
        """Runs the set of commands."""
        exitcode = 0
        failures = []

        # Print a blank line
        printer.fprint()

        # Execute each command and report status
        for name in self.commands:
            command = self.commands[name]
            description = '%s ' % command.get('description', name)[:68]
            printer.fprint(description.ljust(69, '.'), 'bold', inline=True)

            output, status = execute_command(command)

            if status == self.SUCCESS:
                printer.fprint(' [SUCCESS]', 'green', 'bold')
            elif status == self.FAILURE:
                printer.fprint(' [FAILURE]', 'red', 'bold')
                failures.append({'description': description, 'output': output})
                exitcode = 1
            else:
                printer.fprint(' [SKIPPED]', 'cyan', 'bold')

        # Iterate through failures if they exist and print output
        if failures:
            for failure in failures:
                if failure['output']:
                    printer.fprint()
                    printer.fprint(''.ljust(79, '='), 'bold')
                    printer.fprint('FAILED: ' + failure['description'], 'bold')
                    printer.fprint(''.ljust(79, '='), 'bold')
                    printer.fprint(failure['output'])

        # Print a blank line
        printer.fprint()

        exit(exitcode)
