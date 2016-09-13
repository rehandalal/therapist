NOT_GIT_REPO_MSG = '#{red}Not a git repository (or any of the parent directories)'

HOOK_ALREADY_INSTALLED_MSG = 'The pre-commit hook has already been installed.'

EXISTING_HOOK_MSG = ('#{yellow}There is an existing pre-commit hook.\n'
                     '#{reset_all}Therapist can preserve this legacy hook and run it before the Therapist pre-commit '
                     'hook.')

CONFIRM_PRESERVE_LEGACY_HOOK_MSG = 'Would you like to preserve this legacy hook?'

COPYING_HOOK_MSG = 'Copying `pre-commit` to `pre-commit.legacy`...\t'

DONE_COPYING_HOOK_MSG = '#{green}#{bright}DONE'

CONFIRM_REPLACE_HOOK_MSG = 'Do you want to replace this hook?'

INSTALL_ABORTED_MSG = 'Installation aborted.'

INSTALLING_HOOK_MSG = 'Installing pre-commit hook...\t'

DONE_INSTALLING_HOOK_MSG = '#{green}#{bright}DONE'

NO_HOOK_INSTALLED_MSG = 'There is no pre-commit hook currently installed.'

UNINSTALL_ABORTED_MSG = 'Uninstallation aborted.'

CONFIRM_UNINSTALL_HOOK_MSG = 'Are you sure you want to uninstall the current pre-commit hook?'

CURRENT_HOOK_NOT_THERAPIST_MSG = ('#{yellow}The current pre-commit hook is not the Therapist pre-commit hook.\n'
                                  '#{reset_all}Uninstallation aborted.')

LEGACY_HOOK_EXISTS_MSG = '#{yellow}There is a legacy pre-commit hook present.'

CONFIRM_RESTORE_LEGACY_HOOK_MSG = 'Would you like to restore the legacy hook?'

COPYING_LEGACY_HOOK_MSG = 'Copying `pre-commit.legacy` to `pre-commit`...\t'

DONE_COPYING_LEGACY_HOOK_MSG = '#{green}#{bright}DONE'

REMOVING_LEGACY_HOOK_MSG = 'Removing `pre-commit.legacy`...\t'

DONE_REMOVING_LEGACY_HOOK_MSG = '#{green}#{bright}DONE'

UNINSTALLING_HOOK_MSG = 'Uninstalling pre-commit hook...\t'

DONE_UNINSTALLING_HOOK_MSG = '#{green}#{bright}DONE'

MISCONFIGURED_MSG = '#{{red}}Misconfigured: {}'

UNSTAGED_CHANGES_MSG = '#{yellow}You have unstaged changes.'
