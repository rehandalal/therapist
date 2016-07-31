import re

import pytest

from click.testing import CliRunner

from therapist import cli
from therapist._version import __version__
from therapist.context_managers import chdir

from . import Project


@pytest.fixture(scope='class')
def cli_runner():
    return CliRunner()


class TestCLI(object):
    def test_cli_no_options(self, cli_runner):
        result = cli_runner.invoke(cli.cli)
        assert not result.output
        assert not result.exception
        assert result.exit_code == 0

    def test_cli_with_version_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ['--version'])
        assert not result.exception
        assert result.exit_code == 0
        assert 'v{}'.format(__version__) in result.output

    def test_cli_with_help_option(self, cli_runner):
        result = cli_runner.invoke(cli.cli, ['--help'])
        assert 'Usage:' in result.output
        assert not result.exception
        assert result.exit_code == 0


class TestInstall(object):
    def test_install(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            result = cli_runner.invoke(cli.install)
        assert 'Installing pre-commit hook...' in result.output
        assert not result.exception
        assert result.exit_code == 0
        assert p.exists('.git/hooks/pre-commit')

    def test_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.install)
        assert 'Unable to locate git repo.' in result.output
        assert result.exception
        assert result.exit_code == 1

    def test_try_reinstall(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            result = cli_runner.invoke(cli.install)
            assert 'The pre-commit hook has already been installed.' in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_update_outdated(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            hook = p.read('.git/hooks/pre-commit')
            hook_hash = cli.get_hook_hash(p.abspath('.git/hooks/pre-commit'))

            p.write('.git/hooks/pre-commit', hook.replace('# THERAPIST {}'.format(hook_hash), '# THERAPIST n0tth3h45h'))

            result = cli_runner.invoke(cli.install, input='y')
            assert 'You are not using the current version of the pre-commit hook.' in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = p.read('.git/hooks/pre-commit')
            assert '# THERAPIST {}'.format(hook_hash) in hook

    def test_dont_update_outdated(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            hook = p.read('.git/hooks/pre-commit')
            hook_hash = cli.get_hook_hash(p.abspath('.git/hooks/pre-commit'))

            p.write('.git/hooks/pre-commit', hook.replace('# THERAPIST {}'.format(hook_hash), '# THERAPIST n0tth3h45h'))

            result = cli_runner.invoke(cli.install, input='n')
            assert 'Installation aborted.' in result.output
            assert result.exception
            assert result.exit_code == 1

            hook = p.read('.git/hooks/pre-commit')
            assert '# THERAPIST n0tth3h45h'.format(hook_hash) in hook

    def test_preserve_existing(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit', '')
            hook = p.read('.git/hooks/pre-commit')
            assert hook == ''

            result = cli_runner.invoke(cli.install, input='y')
            assert 'There is an existing pre-commit hook.' in result.output
            assert 'Copying `pre-commit` to `pre-commit.legacy`...' in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = p.read('.git/hooks/pre-commit')
            assert '# THERAPIST' in hook

            assert p.exists('.git/hooks/pre-commit.legacy')

    def test_replace_existing(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit', '')
            hook = p.read('.git/hooks/pre-commit')
            assert hook == ''

            result = cli_runner.invoke(cli.install, input='n\ny')
            assert 'There is an existing pre-commit hook.' in result.output
            assert 'Copying `pre-commit` to `pre-commit.legacy`...' not in result.output
            assert not result.exception
            assert result.exit_code == 0

            hook = p.read('.git/hooks/pre-commit')
            assert '# THERAPIST' in hook

    def test_replace_existing_cancel(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit', '#!usr/bin/env bash\n\nexit 1')
            hook = p.read('.git/hooks/pre-commit')
            assert hook == '#!usr/bin/env bash\n\nexit 1'

            result = cli_runner.invoke(cli.install, input='n\nn')
            assert 'There is an existing pre-commit hook.' in result.output
            assert result.exception
            assert result.exit_code == 1

            hook = p.read('.git/hooks/pre-commit')
            assert hook == '#!usr/bin/env bash\n\nexit 1'

    def test_force_option(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit', '# legacy')

            result = cli_runner.invoke(cli.install, ['-f'])
            assert 'There is an existing pre-commit hook.' not in result.output
            assert 'Installing pre-commit hook...' in result.output
            assert not result.exception
            assert result.exit_code == 0

            assert not p.exists('.git/hooks/pre-commit.legacy')

    def test_force_option_preserve_legacy(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit', '# legacy')

            result = cli_runner.invoke(cli.install, ['-f', '--preserve-legacy'])
            assert 'There is an existing pre-commit hook.' not in result.output
            assert 'Copying `pre-commit` to `pre-commit.legacy`...' in result.output
            assert 'Installing pre-commit hook...' in result.output
            assert not result.exception
            assert result.exit_code == 0

            assert '# legacy' in p.read('.git/hooks/pre-commit.legacy')

    def test_force_already_installed(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            result = cli_runner.invoke(cli.install, ['-f'])
            assert 'The pre-commit hook has already been installed.' in result.output
            assert not result.exception
            assert result.exit_code == 0


class TestUninstall(object):
    def test_uninstall(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            result = cli_runner.invoke(cli.uninstall, input='y')
            assert 'Are you sure you want to uninstall the current pre-commit hook?' in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_outside_repo(self, cli_runner, tmpdir):
        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.uninstall)
            assert 'Unable to locate git repo.' in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_no_hook(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            result = cli_runner.invoke(cli.uninstall)
            assert 'There is no pre-commit hook currently installed.' in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_cancel(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            result = cli_runner.invoke(cli.uninstall, input='n')
            assert 'Uninstallation aborted.' in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_non_therapist_hook(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            p.write('.git/hooks/pre-commit')

            result = cli_runner.invoke(cli.uninstall)
            assert 'The current pre-commit hook is not the Therapist pre-commit hook.' in result.output
            assert result.exception
            assert result.exit_code == 1

    def test_restore_legacy(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert '# THERAPIST' in p.read('.git/hooks/pre-commit')

            p.write('.git/hooks/pre-commit.legacy', '# legacy')

            result = cli_runner.invoke(cli.uninstall, input='y\ny')
            assert 'Would you like to restore the legacy hook?' in result.output
            assert 'Copying `pre-commit.legacy` to `pre-commit`...' in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert '# legacy' in p.read('.git/hooks/pre-commit')

    def test_remove_legacy(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert '# THERAPIST' in p.read('.git/hooks/pre-commit')

            p.write('.git/hooks/pre-commit.legacy', '# legacy')

            result = cli_runner.invoke(cli.uninstall, input='y\nn\ny')
            assert 'Would you like to restore the legacy hook?' in result.output
            assert 'Would you like to remove the legacy hook?' in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not p.exists('.git/hooks/pre-commit')
            assert not p.exists('.git/hooks/pre-commit.legacy')

    def test_dont_restore_or_remove_legacy(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert '# THERAPIST' in p.read('.git/hooks/pre-commit')

            p.write('.git/hooks/pre-commit.legacy', '# legacy')

            result = cli_runner.invoke(cli.uninstall, input='y\nn\nn')
            assert 'Would you like to restore the legacy hook?' in result.output
            assert 'Would you like to remove the legacy hook?' in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not p.exists('.git/hooks/pre-commit')
            assert p.exists('.git/hooks/pre-commit.legacy')

    def test_force_option(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            p.write('.git/hooks/pre-commit.legacy', '# legacy')

            result = cli_runner.invoke(cli.uninstall, ['-f'])
            assert 'Are you sure you want to uninstall the current pre-commit hook?' not in result.output
            assert 'There is a legacy pre-commit hook present.' not in result.output
            assert 'Copying `pre-commit.legacy` to `pre-commit`...' not in result.output
            assert 'Removing `pre-commit.legacy`...' in result.output
            assert 'Uninstalling pre-commit hook...' in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert not p.exists('.git/hooks/pre-commit')
            assert not p.exists('.git/hooks/pre-commit.legacy')

    def test_force_option_restore_legacy(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            assert p.exists('.git/hooks/pre-commit')

            p.write('.git/hooks/pre-commit.legacy', '# legacy')

            result = cli_runner.invoke(cli.uninstall, ['-f', '--restore-legacy'])
            assert 'Are you sure you want to uninstall the current pre-commit hook?' not in result.output
            assert 'There is a legacy pre-commit hook present.' not in result.output
            assert 'Copying `pre-commit.legacy` to `pre-commit`...' in result.output
            assert 'Removing `pre-commit.legacy`...' not in result.output
            assert 'Uninstalling pre-commit hook...' not in result.output
            assert not result.exception
            assert result.exit_code == 0
            assert '# legacy' in p.read('.git/hooks/pre-commit')
            assert not p.exists('.git/hooks/pre-commit.legacy')

    def test_force_option_not_therapist_hook(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        with chdir(p.path):
            cli_runner.invoke(cli.install)
            p.write('.git/hooks/pre-commit', '# SOME OTHER HOOK')

            result = cli_runner.invoke(cli.uninstall, ['-f'])
            assert 'Uninstallation aborted.' in result.output
            assert result.exception
            assert result.exit_code == 1
            assert p.exists('.git/hooks/pre-commit')


class TestRun(object):
    def test_run(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert re.search('Linting.+?\[SUCCESS]', result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_outside_repo(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(tmpdir.strpath):
            result = cli_runner.invoke(cli.run)
        assert 'Unable to locate git repo.' in result.output
        assert result.exception
        assert result.exit_code == 1

    def test_fails(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_action(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'lint'])
            assert re.search('Linting.+?\[SUCCESS]', result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_action_fails(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'lint'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_action_invalid(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['-a', 'notanaction'])
            assert 'Available actions:' in result.output
            assert 'lint' in result.output
            assert not result.exception
            assert result.exit_code == 0

    def test_on_file(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['*.py'])
            assert re.search('Linting.+?\[SUCCESS]', result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_on_file_fail(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['*.py'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_pass_dir(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('dir/pass.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['dir'])
            assert re.search('Linting.+?\[SUCCESS]', result.output)
            assert not result.exception
            assert result.exit_code == 0

    def test_pass_dir_fail(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('dir/fail.py')
        p.git.add('.')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run, ['dir'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_include_untracked(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ['--include-untracked'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_include_unstaged(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')
        p.git.commit(m='Add file.')
        p.write('fail.py', 'x')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert not result.exception
            assert result.exit_code == 0

            result = cli_runner.invoke(cli.run, ['--include-unstaged'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_ignore_unstaged_changes(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        p.write('fail.py')
        p.git.add('.')
        p.write('fail.py', 'x')

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert 'There are unstaged changes.' in result.output
            assert result.exception
            assert result.exit_code == 1

            result = cli_runner.invoke(cli.run, ['--ignore-unstaged-changes'])
            assert re.search('Linting.+?\[FAILURE]', result.output)
            assert result.exception
            assert result.exit_code == 1

    def test_misconfigured(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)
        config_data = p.get_config_data()
        config_data.pop('actions')
        p.set_config_data(config_data)

        with chdir(p.path):
            result = cli_runner.invoke(cli.run)
            assert 'Misconfigured:' in result.output
            assert result.exception
            assert result.exit_code == 1


class TestHook(object):
    def test_action_failure(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)

        with chdir(p.path):
            cli_runner.invoke(cli.install)
        assert p.exists('.git/hooks/pre-commit')

        p.write('fail.py')
        p.git.add('.')

        out, err = p.git.commit(m='Should not get committed.')
        assert 'FAIL!  {}'.format(p.abspath('fail.py')) in err

        out, err = p.git.status(porcelain=True)
        assert 'fail.py' in out

    def test_action_success(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)

        with chdir(p.path):
            cli_runner.invoke(cli.install)
        assert p.exists('.git/hooks/pre-commit')

        p.write('pass.py')
        p.git.add('.')

        out, err = p.git.commit(m='Add a file.')
        assert '[SUCCESS]' in err

        out, err = p.git.status(porcelain=True)
        assert not out
        assert not err

    def test_legacy_hook(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)

        with chdir(p.path):
            cli_runner.invoke(cli.install)
        assert p.exists('.git/hooks/pre-commit')

        p.write('.git/hooks/pre-commit.legacy', '#!/usr/bin/env bash\necho "LEGACY"')
        p.chmod('.git/hooks/pre-commit.legacy', cli.MODE_775)

        p.write('pass.py')
        p.git.add('.')

        out, err = p.git.commit(m='Add a file.')
        assert 'LEGACY' in err

        out, err = p.git.status(porcelain=True)
        assert not out
        assert not err

    def test_legacy_hook_fails(self, cli_runner, tmpdir):
        p = Project(tmpdir.strpath)

        with chdir(p.path):
            cli_runner.invoke(cli.install)
        assert p.exists('.git/hooks/pre-commit')

        p.write('.git/hooks/pre-commit.legacy', '#!/usr/bin/env bash\nexit 1')
        p.chmod('.git/hooks/pre-commit.legacy', cli.MODE_775)

        p.write('pass.py')
        p.git.add('.')

        p.git.commit(m='Add a file.')

        out, err = p.git.status(porcelain=True)
        assert 'pass.py' in out
        assert not err
