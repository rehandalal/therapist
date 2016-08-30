import pytest

from therapist.collections import Collection


class TestCollection(object):
    def test_str(self):
        items = ['a', 'b', 'c']
        s = Collection(items)
        assert str(s) == str(items)

    def test_repr(self):
        s = Collection()
        assert s.__repr__() == '<Collection>'

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
