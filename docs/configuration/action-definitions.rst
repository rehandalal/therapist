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

:working_dir:
    This is a path to a directory that will be used as the working directory
    when running the action. File paths sent to the action will be rewritten
    relative to the new working directory. This is useful when the action needs
    to be run not from the project root (or the directory where
    ``.therapist.yml`` resides). Make sure any path of your action is relative
    to the new working directory.

:files_root:
    This is a path used to filter down the files passed to the action. Only
    files that are contained within this new root are passed to the action.
