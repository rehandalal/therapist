from therapist.git import Status


class TestStatus(object):
    def test_parsing_from_string(self):
        s = Status.from_string('M  test.py')
        assert s.state == 'M'
        assert not s.is_modified
        assert s.path == 'test.py'
        assert s.original_path is None

        s = Status.from_string('RM test.py -> new_test.py')
        assert s.state == 'R'
        assert s.is_modified
        assert s.path == 'new_test.py'
        assert s.original_path == 'test.py'

    def test_properties(self):
        s = Status.from_string('R  test.py -> new_test.py')
        assert s.is_renamed
        assert s.is_staged
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_untracked

        s = Status.from_string('D  test.py')
        assert s.is_deleted
        assert s.is_staged
        assert not s.is_added
        assert not s.is_renamed
        assert not s.is_untracked

        s = Status.from_string('??  test.py')
        assert s.is_untracked
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_staged

        s = Status.from_string('A  test.py')
        assert s.is_added
        assert s.is_staged
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_untracked

    def test_str(self):
        text = 'R  test.py -> new_test.py'
        s = Status.from_string(text)
        assert s.__str__() == text

    def test_repr(self):
        s = Status.from_string('M  test.py')
        assert s.__repr__() == '<Status test.py>'
