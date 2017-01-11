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
        return out.decode('utf-8'), err.decode('utf-8'), pipes.returncode

    def __getattr__(self, name):
        name = name.replace('_', '-')
        return Git(self.current + [name], repo_path=self.repo_path)

    def __str__(self):  # pragma: no cover
        return str(self.current)

    def __repr__(self):  # pragma: no cover
        return '<Git {}>'.format(str(self))
