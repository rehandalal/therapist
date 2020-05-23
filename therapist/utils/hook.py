import hashlib


def read_hook_hash(path):
    """Verify that the file at path is the therapist hook and return the hash"""
    with open(path, "r") as f:
        f.readline()  # Discard the shebang line
        version_line = f.readline()
        if version_line.startswith("# THERAPIST"):
            return version_line.split()[2]


def read_hook_version(path):
    """Read the hook version from the file."""
    with open(path, "r") as f:
        f.readline()  # Discard the shebang line
        version_line = f.readline()
        if version_line.startswith("# THERAPIST"):
            try:
                return int(version_line.split()[3][1:])
            except IndexError:
                return 1


def calculate_hook_hash(path, options):
    """Hash a hook file"""
    with open(path, "r") as f:
        data = f.read()
        for key in sorted(options.keys()):
            data += "\n#{}={}".format(key, options.get(key))
        return hashlib.md5(data.encode()).hexdigest()
