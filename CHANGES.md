# Changelog

### v2.1.0

- Residual support for Python 2 removed and added official support for
  Python 3.8.
- Add `working_dir` configuration option for actions.
- Add `files_root` configuration option for actions.

### v2.0.1

- Fixes an issue where deleted files were passed to actions when the
  `use-tracked-files` flag was used with the CLI.

### v2.0.0

- **Therapist no longer requires Git.**
  - To maintain backwards compatibility Therapist will behave as it
    previously did if the folder with the `.therapist.yml` file is the
    root of a Git repo.
  - A new `--disable-git` flag can be used to disable git-aware behavior
    when using Therapist in a Git repo.
  - A new `--enable-git` flag can be used to enable git-aware behavior.
- **Dropped support for Python 2.7 and 3.4.**
- The hook is now versioned and Therapist will complain about outdated
  hooks.

### v1.6.0

- **MAJOR BUG FIX**: Therapist now handles copied file correctly.
  Previously it would fail or overwrite the contents of copied files.

### v1.5.0

- Fix an issue with detecting which action modified files.
- Added the ability to configure shortcuts. 
- When `--include-untracked` and `--use-tracked-files` are used
  together the files are correctly selected.

### v1.4.3

- Fix a second issue with false positives in detecting files modified
  by actions.

### v1.4.2

- Fixes an issue with false positives in detecting files modified by
  actions.

### v1.4.1

- Added the `--stage-modified-files` flag to the `run` command. When
  this is used any files modified by the actions will be staged after
  running.
- Added the `--no-stage-modified-files` flag to the `install` command.
  This prevents the default hook behaviour of staging any files
  modified by the hook while it's running.

### v1.4.0

- Added the `--fix` flag to the `run` command to automatically fix
  issues when possible.
- New `fix` parameter for 
  [action definitions](https://therapist.readthedocs.io/en/v1.4.0/configuration.html#action-definitions).
- Added the `--fix` flag to the `install` command to configure the hook
  to use `--fix` with `run`.

### v1.3.2

- Results now show both stdout and stderr details if both are present.

### v1.3.1

- Better support for unicode in results output.

### v1.3.0

- Drops support for Python 3.3.
- Processes are now sorted by name for stable result sets.

### v1.2.1

- Include missing commits due to packaging error.

### v1.2.0

- Fixed [issue #14](https://github.com/rehandalal/therapist/issues/14) 
  which was resulting in permanent loss of files or changes in certain
  edge cases where the stash process fails.

### v1.1.0

- Therapist hook now has the full path to the therapist added during
  installation.

### v1.0.0

- Added a new plugin system which allows for custom linting plugin to be
  written specifically for Therapist.
- Uses [colorama](https://github.com/tartley/colorama) to handle ANSI 
  colors.
- Added the `--no-color` flag to disable colors from being printed in
  the output.
- Added the `--plugin` option to the `run` command to allow configured
  plugins to be run individually.

### v0.3.2

- Added the `--junit-xml` flag to allow for a JUnit XML style report to
  be output to a given path.
- Added the `--quiet` flag that suppresses output from the `run`
  command.

### v0.3.1

- Fix some decoding issues that occur in Python 2.7.
- Using the `--include-unstaged` flag now has the side-effect of setting
  `--include-unstaged-changes` as well.
- If for some reason an error occurs while executing an action we now
  ensure that any stashed changes are restored.

### v0.3

- Pre-commit hook is now a bash script that calls the run command from 
  the CLI.
- CLI can now identify the Therapist pre-commit hook during install and
  uninstall.
- Support for retaining existing pre-commit hook when installing 
  Therapist pre-commit hook.
- Running actions no longer errors out when there files have been 
  modified after they've been staged. Actions are now run against the 
  state of the file that has been cached in the index unless the 
  `--include-unstaged-changes` flag is used in which case actions are
  run against the files in their current state.
- Added the `--use-tracked-files` flag, which allows you to run actions
  against all the files that are being tracked by the repo.
