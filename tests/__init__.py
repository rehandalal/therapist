import os
import shutil
import six
import yaml

from therapist.git import Git


class Project(object):
    """Creates a project that's ready to use for testing."""
    config_data = {}

    def __init__(self, path, config_data=None, *args, **kwargs):
        self.path = os.path.join(os.path.abspath(path), 'project')
        self.config_file = os.path.join(self.path, '.therapist.yml')

        sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_project')
        shutil.copytree(sample_path, self.path)

        # Initialize a git repo and configure
        self.git = Git(repo_path=self.path)
        self.git.init()
        self.git.config('user.name', 'test-suite')
        self.git.config('user.email', 'test-suite@therapist.xyz')

        # Commit all files to the repo
        self.git.add('.')
        self.git.commit(m='Initial commit')

        if config_data:
            self.set_config_data(config_data)

    def get_config_data(self):
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)
        return data

    def set_config_data(self, data):
        with open(self.config_file, 'w+') as f:
            f.write(six.u(yaml.dump(data, default_flow_style=False)))

        # Commit changes to the config file
        self.git.add(self.config_file)
        self.git.commit(m='Update .therapist.yml')

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
