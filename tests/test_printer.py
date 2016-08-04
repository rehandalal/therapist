from therapist import printer


class TestPrinter(object):
    def test_stylize(self):
        assert printer.stylize('test', (printer.RED, printer.BOLD,)) == '\x1b[0m\x1b[1m\x1b[31mtest\x1b[0m'

    def test_fsprint(self, capsys):
        printer.fsprint('test', (printer.RED,))
        out, err = capsys.readouterr()
        assert out == '\x1b[0m\x1b[31mtest\x1b[0m\n'

    def test_fsprint_inline(self, capsys):
        printer.fsprint('test', (printer.RED,), end='')
        out, err = capsys.readouterr()
        assert out == '\x1b[0m\x1b[31mtest\x1b[0m'
