import curses


class Keys(object):
    KEYS_ENTER = (curses.KEY_ENTER, '\n', '\r')
    KEY_SELECT = None  # used for future feature (multi select)
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEYS_DELETE = (curses.KEY_BACKSPACE, '\b', '\x7f')
    KEY_CANC = curses.KEY_DC
    KEY_SHIFT_TAB = curses.KEY_BTAB
    KEY_RIGHT = curses.KEY_RIGHT
    KEY_LEFT = curses.KEY_LEFT
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_TAB = '\t'
    KEY_ESC = '\x1b'  # NOTE: the KEY_ESC can be received with some delay
    KEY_CTRL_A = '\x01'
    KEY_CTRL_E = '\x05'
    KEY_CTRL_S = '\x13'  # not working well on ubuntu 20.04 terminal
    KEY_CTRL_D = '\x04'
    KEY_CTRL_F = '\x06'
    KEY_CTRL_U = '\x15'
    KEY_CTRL_L = '\x0c'
    KEY_CTRL_SPACE = '\x00'
    KEY_START = curses.KEY_HOME
    KEY_END = curses.KEY_END
    KEYS_EDIT = ('e', 'E')
    KEY_TAG = '#'
    KEY_AT = '@'
    KEY_TIMEOUT = curses.ERR