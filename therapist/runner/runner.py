import os

from therapist.utils.git import Git, Status


class Runner(object):
    def __init__(self, cwd, files=None, **kwargs):
        # Options from kwargs:
        fix = kwargs.get("fix", False)

        # Git related options
        enable_git = kwargs.get("enable_git", False)
        include_unstaged = kwargs.get("include_unstaged", False)
        include_untracked = kwargs.get("include_untracked", False)
        include_unstaged_changes = kwargs.get("include_unstaged_changes", False)
        stage_modified_files = kwargs.get("stage_modified_files", False)

        self.cwd = os.path.abspath(cwd)
        self.unstaged_changes = False

        self.git = Git(repo_path=self.cwd) if enable_git else None
        self.include_unstaged_changes = include_unstaged_changes or include_unstaged
        self.fix = fix
        self.stage_modified_files = stage_modified_files
        self.file_mtimes = {}

        if files is None:
            files = []

            if self.git:
                untracked_files = "all" if include_untracked else "no"
                out, err, code = self.git.status(porcelain=True, untracked_files=untracked_files)

                for line in out.splitlines():
                    file_status = Status(line)

                    # Check if staged files were modified since being staged
                    if file_status.is_staged and file_status.is_modified:
                        self.unstaged_changes = True

                    # Skip unstaged files if the `unstaged` flag is False
                    if not file_status.is_staged and not include_unstaged and not include_untracked:
                        continue

                    # Skip deleted files
                    if file_status.is_deleted:
                        continue

                    files.append(file_status.path)

        for path in files:
            if os.path.exists(path):
                self.file_mtimes[path] = os.path.getmtime(path)

        self.files = files

    def run_process(self, process):
        """Runs a single action."""
        message = u"#{bright}"
        message += u"{} ".format(str(process)[:68]).ljust(69, ".")

        stashed = False
        if self.git and self.unstaged_changes and not self.include_unstaged_changes:
            out, err, code = self.git.stash(keep_index=True, quiet=True)
            stashed = code == 0

        try:
            result = process(files=self.files, cwd=self.cwd, fix=self.fix)

            # Check for modified files
            if self.git:
                out, err, code = self.git.status(porcelain=True, untracked_files="no")
                for line in out.splitlines():
                    file_status = Status(line)

                    # Make sure the file is one of the files that was processed
                    if file_status.path in self.files and file_status.is_modified:
                        mtime = (
                            os.path.getmtime(file_status.path)
                            if os.path.exists(file_status.path)
                            else 0
                        )
                        if mtime > self.file_mtimes.get(file_status.path, 0):
                            self.file_mtimes[file_status.path] = mtime
                            result.add_modified_file(file_status.path)
                            if self.stage_modified_files:
                                self.git.add(file_status.path)
            else:
                for path in self.files:
                    mtime = os.path.getmtime(path) if os.path.exists(path) else 0
                    if mtime > self.file_mtimes.get(path, 0):
                        result.add_modified_file(path)

        except:  # noqa: E722
            raise
        finally:
            if stashed and self.git:
                self.git.reset(hard=True, quiet=True)
                self.git.stash.pop(index=True, quiet=True)

        if result.is_success:
            message += u" #{green}[SUCCESS]"
        elif result.is_failure:
            message += u" #{red}[FAILURE]"
        elif result.is_skip:
            message += u" #{cyan}[SKIPPED]"
        elif result.is_error:
            message += u" #{red}[ERROR!!]"

        return result, message
