import re


class Status(object):
    def __init__(self, status):
        matches = re.search(r"^((?:[MADRCU ?!]){2}) (.+?)(?: -> (.+?))?$", status)
        self.x = matches[1][0]
        self.y = matches[1][1]
        self.path = matches[3] if matches[3] else matches[2]
        self.original_path = matches[2] if matches[3] else None

    def __str__(self):
        status = "{}{}".format(self.x, self.y)
        if self.original_path:
            status = "{} {} -> {}".format(status, self.original_path, self.path)
        else:
            status = "{} {}".format(status, self.path)
        return status

    def __repr__(self):  # pragma: no cover
        return "<Status {}>".format(self.path)

    @property
    def is_staged(self):
        return self.x not in (" ", "?", "!")

    @property
    def is_untracked(self):
        return self.x == "?"

    @property
    def is_ignored(self):
        return self.x == "!"
