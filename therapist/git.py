import re


class Status(object):
    def __init__(self, state=None, is_modified=False, path=None, original_path=None):
        self.state = state
        self.path = path
        self.original_path = original_path
        self.is_modified = is_modified

    @classmethod
    def from_string(cls, string):
        status = cls()

        status.state = string[0].strip().upper()
        status.is_modified = string[1].upper() == 'M'

        if status.is_renamed:
            matches = re.search('^(.+?)\s->\s(.+?)$', string[3:])
            status.original_path = matches.groups()[0]
            status.path = matches.groups()[1]
        else:
            status.path = string[3:]

        return status

    @property
    def is_staged(self):
        """If the state is empty then the file is unstaged."""
        return bool(self.state)

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
