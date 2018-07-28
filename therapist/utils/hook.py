import hashlib

from six import iterkeys


def identify_hook(path):
    """Verify that the file at path is the therapist hook and return the hash"""
    with open(path, 'r') as f:
        f.readline()  # Discard the shebang line
        version_line = f.readline()
        if version_line.startswith('# THERAPIST'):
            return version_line.split()[2]


def hash_hook(path, options):
    """Hash a hook file"""
    with open(path, 'r') as f:
        data = f.read()
        for key in sorted(iterkeys(options)):
            data += '\n#{}={}'.format(key, options.get(key))
        return hashlib.md5(data.encode()).hexdigest()
