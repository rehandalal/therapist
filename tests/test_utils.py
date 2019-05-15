from therapist.utils import parse_version, version_compare
from therapist.utils.git import Status


class TestGitStatus(object):
    def test_parsing_from_string(self):
        s = Status("M  test.py")
        assert s.state == "M"
        assert not s.is_modified
        assert s.path == "test.py"

        s = Status("RM test.py -> new_test.py")
        assert s.state == "R"
        assert s.is_modified
        assert s.path == "new_test.py"
        assert s.original_path == "test.py"

    def test_properties(self):
        s = Status("R  test.py -> new_test.py")
        assert s.is_renamed
        assert s.is_staged
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_untracked
        assert not s.is_copied

        s = Status("C  test.py -> new_test.py")
        assert s.is_copied
        assert s.is_staged
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_untracked
        assert not s.is_renamed

        s = Status("D  test.py")
        assert s.is_deleted
        assert s.is_staged
        assert not s.is_added
        assert not s.is_renamed
        assert not s.is_untracked
        assert not s.is_copied

        s = Status("??  test.py")
        assert s.is_untracked
        assert not s.is_added
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_staged
        assert not s.is_copied

        s = Status("A  test.py")
        assert s.is_added
        assert s.is_staged
        assert not s.is_deleted
        assert not s.is_renamed
        assert not s.is_untracked
        assert not s.is_copied

    def test_str(self):
        text = "R  test.py -> new_test.py"
        s = Status(text)
        assert s.__str__() == text

        text = "C  test.py -> new_test.py"
        s = Status(text)
        assert s.__str__() == text

        text = "AM  test.py"
        s = Status(text)
        assert s.__str__() == text


class TestVersionComparator(object):
    def test_parse_version(self):
        assert parse_version("3") == [3, 0, 0]
        assert parse_version("3.1") == [3, 1, 0]
        assert parse_version("3.1.2") == [3, 1, 2]
        assert parse_version(3.2) == [3, 2, 0]

    def test_version_compare(self):
        assert version_compare("1.5.5", "1.5.5") == 0
        assert version_compare("2.0.0", "1.5.5") == 1
        assert version_compare("0.1.0", "1.5.5") == -1
        assert version_compare("1.6.0", "1.5.5") == 1
        assert version_compare("1.1.0", "1.5.5") == -1
        assert version_compare("1.5.6", "1.5.5") == 1
        assert version_compare("1.5.1", "1.5.5") == -1
