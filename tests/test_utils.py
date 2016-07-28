import os

from therapist.utils import chdir, fnmatch_any


class TestUtils(object):
    def test_fnmatch_any_single(self):
        assert fnmatch_any('dir/test.py', '*.py')
        assert not fnmatch_any('test.js', '*.py')

    def test_fnmatch_any_multiple(self):
        assert fnmatch_any('dir/test.py', ['dir/*', '*.js'])
        assert not fnmatch_any('test.js', ['dir/*', '*.py'])

    def test_chdir(self):
        cwd = os.path.abspath(os.curdir)
        fwd = os.path.abspath(os.path.join(cwd, '..'))
        with chdir(fwd):
            assert os.path.abspath(os.curdir) == fwd
        assert os.path.abspath(os.curdir) == cwd
