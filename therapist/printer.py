from six import print_


RESET = '\x1b[0m'
BOLD = '\x1b[1m'
UNDERLINE = '\x1b[4m'
BLINK = '\x1b[5m'
BLACK = '\x1b[30m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
MAGENTA = '\x1b[35m'
CYAN = '\x1b[36m'
GRAY = '\x1b[37m'


def stylize(text, styles=()):
    """Returns a string with the styles applied."""
    for style in styles:
        text = '{}{}'.format(style, text)

    text = '{}{}{}'.format(RESET, text, RESET)

    return text


def fsprint(text='', styles=(), **kwargs):
    """Prints a string with the font styles applied."""
    print_(stylize(text, styles), **kwargs)
