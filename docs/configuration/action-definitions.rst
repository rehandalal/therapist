Action definitions
==================

There are several optional parameters that you can specify for a action. They
are:

:run:
    This is the actual command to be run. You may use the named placeholder
    ``{files}`` which be replaced with a space-separated list of files that
    were modified and added to the commit.

:fix:
    This is the command to be run when the ``--fix`` option is used. You may
    use the named placeholder ``{files}`` which be replaced with a
    space-separated list of files that were modified and added to the commit.

:description:
    A short description of the command that is used to identify the command in
    the output. If it is longer than 68 characters, it will be truncated. If
    no description is provided it will default to the name of the command.

:include:
    This can be a single string or list strings of UNIX filename patterns.
    Files that match *any* of the patterns will be passed through to the
    command through ``{files}`` unless they match a pattern in the exclude
    parameter.

:exclude:
    This can be a single string or a list of strings of UNIX filename patterns.
    Files that match *any* of the patterns will never be passed through to the
    command through ``{files}``.
