import os
import shutil

from contextlib import contextmanager

import six
import yaml

from therapist.plugins import Plugin
from therapist.runner.result import Result
from therapist.utils.git import Git


@contextmanager
def chdir(path):
    cwd = os.path.abspath(os.curdir)
    os.chdir(path)
    yield
    os.chdir(cwd)


class Project(object):
    """Creates a project that's ready to use for testing."""
    config_data = {}

    def __init__(self, path, config_data=None, *args, **kwargs):
        self.path = os.path.join(os.path.abspath(path), 'project')
        self.config_file = os.path.join(self.path, '.therapist.yml')

        blank = kwargs.get('blank', False)

        if not blank:
            sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_project')
            shutil.copytree(sample_path, self.path)
        else:
            os.makedirs(self.path)

        # Initialize a git repo and configure
        self.git = Git(repo_path=self.path)
        self.git.init()
        self.git.config('user.name', 'test-suite')
        self.git.config('user.email', 'test-suite@therapist.xyz')
        self.git.config('commit.gpgsign', 'false')

        if not blank:
            # Commit all files to the repo
            self.git.add('.')
            self.git.commit(m='Initial commit')

            if config_data:
                self.set_config_data(config_data)

    def get_config_data(self):
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)
        return data

    def set_config_data(self, data, commit=True):
        with open(self.config_file, 'w+') as f:
            f.write(six.u(yaml.dump(data, default_flow_style=False)))

        if commit:
            # Commit changes to the config file
            self.git.add(self.config_file)
            self.git.commit(m='Update .therapist.yml')

    def abspath(self, path):
        """Converts a path relative to the project root to an absolute path."""
        return os.path.abspath(os.path.join(self.path, path))

    def exists(self, path):
        """Checks if a file exists."""
        return os.path.exists(os.path.join(self.path, path))

    def makedirs(self, path):
        """Makes dirs recursively."""
        path = os.path.join(self.path, path)
        if not self.exists(path):
            os.makedirs(path)

    def write(self, path, s=''):
        """Write to a file."""
        path = os.path.join(self.path, path)
        self.makedirs(os.path.dirname(path))
        with open(path, 'w+') as f:
            f.write(s)

    def read(self, path):
        """Read a file."""
        path = os.path.join(self.path, path)
        with open(path, 'r') as f:
            s = f.read()
        return s

    def remove(self, path, recursive=False):
        """Removes a file or a directory if recursive is True."""
        path = os.path.join(self.path, path)
        if os.path.isdir(path) and recursive:
            for stats in os.walk(path):
                for f in stats[2]:
                    os.remove(os.path.join(stats[0], f))
        else:
            os.remove(path)

    def copy(self, src, dst):
        """Copy a file from one path to another"""
        src = os.path.join(self.path, src)
        dst = os.path.join(self.path, dst)
        shutil.copy2(src, dst)

    def chmod(self, path, mode):
        """Modify file permissions."""
        path = os.path.join(self.path, path)
        os.chmod(path, mode)


class SimplePlugin(Plugin):
    """A very basic implementation of a plugin."""

    def execute(self, **kwargs):
        files = kwargs.get('files')
        result = Result(self)

        for filename in files:
            with open(filename, 'r') as f:
                if 'PLUGIN: FAIL' in f.read():
                    result.mark_complete(status=Result.FAILURE, output='', error='')
                    return result

        result.mark_complete(status=Result.SUCCESS)
        return result
