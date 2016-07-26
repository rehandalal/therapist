from six import print_


class Printer(object):
    STYLES = {
        'RESET': '\x1b[0m',
        'BOLD': '\x1b[1m',
        'UNDERLINE': '\x1b[4m',
        'BLINK': '\x1b[5m',
        'BLACK': '\x1b[30m',
        'RED': '\x1b[31m',
        'GREEN': '\x1b[32m',
        'YELLOW': '\x1b[33m',
        'BLUE': '\x1b[34m',
        'MAGENTA': '\x1b[35m',
        'CYAN': '\x1b[36m',
        'GRAY': '\x1b[37m',
    }

    def format(self, text, *styles):
        """Returns a string with the styles applied."""
        for style in styles:
            if style.upper() in self.STYLES:
                text = '%s%s' % (self.STYLES[style.upper()], text)

        text = '%s%s%s' % (self.STYLES['RESET'], text, self.STYLES['RESET'])

        return text

    def fprint(self, text='', *styles, **kwargs):
        """Prints a string with the styles applied."""
        end = '' if kwargs.get('inline', False) else '\n'
        print_(self.format(text, *styles), end=end)
