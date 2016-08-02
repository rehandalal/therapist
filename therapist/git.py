import re
import subprocess


def to_cli_args(*args, **kwargs):
    cmd = []
    for k, v in kwargs.items():
        k = k.replace('_', '-')
        short = len(k) == 1
        if short:
            cmd.append('-' + k)
            if v is not True:
                cmd.append(v)
        else:
            if v is True:
                cmd.append('--' + k)
            else:
                cmd.append('--{0}={1}'.format(k, v))

    cmd.extend(args)
    return cmd


class Git(object):
    def __init__(self, cmd=None, repo_path=None):
        self.repo_path = repo_path
        self.current = list(cmd) if cmd else ['git']

    def __call__(self, *args, **kwargs):
        cmd = self.current + to_cli_args(*args, **kwargs)

        subprocess_kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE
        }

        if self.repo_path:
            subprocess_kwargs['cwd'] = self.repo_path

        pipes = subprocess.Popen(cmd, **subprocess_kwargs)
        out, err = pipes.communicate()
        return out.decode(), err.decode()

    def __getattr__(self, name):
        name = name.replace('_', '-')
        return Git(self.current + [name], repo_path=self.repo_path)

    def __str__(self):
        return str(self.current)

    def __repr__(self):
        return '<Git {}>'.format(str(self))


class Status(object):
    def __init__(self, state=None, is_modified=False, path=None, original_path=None):
        self.state = state
        self.path = path
        self.original_path = original_path
        self.is_modified = is_modified

    def __str__(self):
        status = '{:1}{:1}'.format(self.state, 'M' if self.is_modified else '')
        if self.is_renamed:
            status = '{:3}{} -> {}'.format(status, self.original_path, self.path)
        else:
            status = '{:3}{}'.format(status, self.path)
        return status

    def __repr__(self):
        return '<Status {}>'.format(self.path)

    @classmethod
    def from_string(cls, string):
        string = string  # Ensure that the string is actually a string
        status = cls()

        status.state = string[0]
        status.is_modified = string[1] == 'M'

        if status.is_renamed:
            matches = re.search('(\S+?)\s+->\s+(\S+?)$', string[3:])
            status.original_path = matches.groups()[0]
            status.path = matches.groups()[1]
        else:
            status.path = string[3:]

        return status

    @property
    def is_staged(self):
        """If the state is empty then the file is unstaged."""
        return self.state not in (' ', '?',)

    @property
    def is_untracked(self):
        """Returns true if the file is untracked."""
        return self.state == '?'

    @property
    def is_renamed(self):
        """Returns true if the file is renamed."""
        return self.state == 'R'

    @property
    def is_deleted(self):
        """Returns true if the file is deleted."""
        return self.state == 'D'

    @property
    def is_added(self):
        """Returns true if the file is added."""
        return self.state == 'A'
