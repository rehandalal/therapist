def identify_hook(path):
    """Verify that the file at path is the therapist hook and return the hash"""
    with open(path, 'r') as f:
        f.readline()  # Discard the shebang line
        version_line = f.readline()
        if version_line.startswith('# THERAPIST'):
            return version_line.split()[2]
