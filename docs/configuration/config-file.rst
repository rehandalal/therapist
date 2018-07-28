The configuration file
======================

Once you have the Therapist pre-commit hook installed you will need to
configure the actions that will be run before each commit. This is done with
a ``.therapist.yml`` configuration file.

Add a file called ``.therapist.yml`` to the root directory of your project. The
configuration file describes a set of actions like so:

    .. code-block:: yaml

        actions:
            flake8:
                run: flake8 {files}
                include: "*.py"
                exclude:
                    - "docs\*.py"
                    - "migrations\*.py"
            eslint:
                description: ESLint
                run: yarn eslint {files}
                fix: yarn eslint --fix {files}
                include:
                    - "*.js"
                    - "*.jsx"
