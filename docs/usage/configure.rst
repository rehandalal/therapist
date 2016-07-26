Configuration
=============

The configuration file
----------------------

Once you have the therapist pre-commit hook installed you will need to
configure the commands that will be run before each commit. This is done with
a ``.therapist.yml`` configuration file.

Add a file called ``.therapist.yml`` to the root directory of your project. The
configuration file describes a set of commands like so:

    .. code-block:: yml

        flake8:
            run: flake8 {files}
            include: "*.py"
            exclude:
                - "docs\*.py"
                - "migrations\*.py"
        eslint:
            description: ESLint
            run: ./node_modules/bin/eslint {files}
            include:
                - "*.js"
                - "*.jsx"


The command parameters
----------------------

There are several parameters that you can set for a command. They are:

run
    This is the actual command to be run. You may use the named placeholder
    ``{fields}`` which be replaced with a space-separated list of files that
    were modified and added to the commit.

description
    *(Optional)*
    A short description of the command that is used to identify the command in
    the output. If it is longer than 68 characters, it will be truncated. If
    no description is provided it will default to the name of the command.

include
    *(Optional)*
    This can be a single string or list strings of UNIX filename patterns.
    Files that match *any* of the patterns will be passed through to the
    command through ``{fields}`` unless they match a pattern in the exclude
    parameter.

exclude
    *(Optional)*
    This can be a single string or a list of strings of UNIX filename patterns.
    Files that match *any* of the patterns will never be passed through to the
    command through ``{fields}``.
