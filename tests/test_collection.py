import pytest

from therapist.collection import Collection


class TestCollection(object):
    def test_append(self):
        s = Collection()
        assert len(s.objects) == 0

        s.append('item')
        assert len(s.objects) == 1
        assert s[0] == 'item'

    def test_object_class(self):
        class BooleanCollection(Collection):
            class Meta:
                object_class = bool

        s = BooleanCollection([True])

        with pytest.raises(TypeError):
            s.append('True')

    def test_bool(self):
        s = Collection()
        assert not bool(s)

        s.append('item')
        assert bool(s)
