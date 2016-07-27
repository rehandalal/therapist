import pytest

from therapist.printer import Printer


@pytest.fixture(scope='class')
def printer():
    return Printer()


class TestPrinter(object):
    def test_format(self, printer):
        assert printer.format('test', 'red', 'bold') == '\x1b[0m\x1b[1m\x1b[31mtest\x1b[0m'

    def test_fprint(self, printer, capsys):
        printer.fprint('test', 'red')
        out, err = capsys.readouterr()
        assert out == '\x1b[0m\x1b[31mtest\x1b[0m\n'

    def test_fprint_inline(self, printer, capsys):
        printer.fprint('test', 'red', inline=True)
        out, err = capsys.readouterr()
        assert out == '\x1b[0m\x1b[31mtest\x1b[0m'
