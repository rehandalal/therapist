import os

from therapist.context_managers import chdir


class TestContextManagers(object):
    def test_chdir(self):
        cwd = os.path.abspath(os.curdir)
        fwd = os.path.abspath(os.path.join(cwd, '..'))
        with chdir(fwd):
            assert os.path.abspath(os.curdir) == fwd
        assert os.path.abspath(os.curdir) == cwd
