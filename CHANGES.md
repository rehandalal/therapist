# Changelog

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
