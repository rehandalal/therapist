from therapist.utils import fnmatch_any


class TestUtils(object):
    def test_fnmatch_any_single(self):
        assert fnmatch_any('dir/test.py', '*.py')
        assert not fnmatch_any('test.js', '*.py')

    def test_fnmatch_any_multiple(self):
        assert fnmatch_any('dir/test.py', ['dir/*', '*.js'])
        assert not fnmatch_any('test.js', ['dir/*', '*.py'])
