import re


class Status(object):
    def __init__(self, state=None, modified=False, path=None, original_path=None):
        self.state = state
        self.path = path
        self.original_path = original_path
        self.modified = modified

    @classmethod
    def from_string(cls, string):
        status = cls()

        status.state = string[0].strip().upper()
        status.modified = string[1].upper() == 'M'

        if status.state == 'R':
            matches = re.search('^(.+?)\s->\s(.+?)$', string[3:])
            status.original_path = matches.groups()[0]
            status.path = matches.groups()[1]
        else:
            status.path = string[3:]

        return status
