from therapist.utils.git import Status


class TestGitStatus(object):
    def test_parsing_from_string(self):
        s = Status('M  test.py')
        assert s.state == 'M'
        assert not s.is_modified
        assert s.path == 'test.py'

        s = Status('RM test.py -> new_test.py')
        assert s.state == 'R'
        assert s.is_modified
        assert s.path == 'new_test.py'
        assert s.original_path == 'test.py'

    def test_properties(self):
        s = Status('R  test.py -> new_test.py')
        assert s.is_renamed
        assert s.is_staged
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_untracked

        s = Status('D  test.py')
        assert s.is_deleted
        assert s.is_staged
        assert not s.is_added
        assert not s.is_renamed
        assert not s.is_untracked

        s = Status('??  test.py')
        assert s.is_untracked
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_staged

        s = Status('A  test.py')
        assert s.is_added
        assert s.is_staged
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_untracked

    def test_str(self):
        text = 'R  test.py -> new_test.py'
        s = Status(text)
        assert s.__str__() == text

        text = 'AM  test.py'
        s = Status(text)
        assert s.__str__() == text