import curses
import logging


class Drawer(object):
    """
    Class to handle the console drawer
    """
    _TEXT_TO_LONG = ".."

    ID_COLOR_RED_BLACK = 1
    ID_COLOR_BLUE_BLACK = 2
    ID_COLOR_GREEN_BLACK = 3
    ID_COLOR_RED_WHITE = 4
    ID_COLOR_BLUE_WHITE = 5
    ID_COLOR_WHITE_BLACK = 6
    ID_COLOR_BLACK_GREEN = 7
    NULL_COLOR = 1

    def __init__(self, screen):
        self.terminal_screen = screen
        self.max_y, self.max_x = self.terminal_screen.getmaxyx()
        self.x = 0
        self.y = 0
        # TODO decide if split this in separated class
        self.shifted = 0

        # define colors
        self.color_search = None
        self.color_hash_tag = None
        self.color_border = None
        self.color_selected_row = None
        self.color_selector = None
        self.color_columns_title = None
        self.init_colors()

    def init_colors(self):
        """
        define and set console colors
        :return:
        """
        # use the default colors of the terminal
        curses.use_default_colors()

        curses.init_pair(self.ID_COLOR_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.ID_COLOR_BLUE_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(self.ID_COLOR_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.ID_COLOR_WHITE_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)

        curses.init_pair(self.ID_COLOR_RED_WHITE, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(self.ID_COLOR_BLUE_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.init_pair(self.ID_COLOR_BLACK_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)

        # set colors
        self.color_search = curses.color_pair(self.ID_COLOR_BLUE_WHITE)
        self.color_hash_tag = curses.color_pair(self.ID_COLOR_WHITE_BLACK)
        self.color_border = curses.color_pair(self.ID_COLOR_GREEN_BLACK)
        self.color_selected_row = curses.color_pair(self.ID_COLOR_GREEN_BLACK) | curses.A_BOLD
        self.color_selector = curses.color_pair(self.ID_COLOR_GREEN_BLACK)
        self.color_columns_title = curses.color_pair(self.ID_COLOR_BLACK_GREEN)

    def hide_cursor(self):
        """
        hide the cursor
        :return:
        """
        curses.curs_set(0)
        pass

    def show_cursor(self):
        """
        show the cursor
        :return:
        """
        curses.curs_set(1)
        pass

    def wait_next_char(self):
        """
        wait input from user
        :return:
        """
        c = self.terminal_screen.getch()
        return c

    def clear(self):
        """
        Clear screen
        :return:
        """
        self.terminal_screen.clear()

    def refresh(self):
        """
        Refresh screen
        :return:
        """
        self.terminal_screen.refresh()

    def reset(self):
        """
        call refresh to clean the screen ?
        :return:
        """
        self.x = 0
        self.y = 0
        self.max_y, self.max_x = self.terminal_screen.getmaxyx()

    def move_cursor(self, x, y):
        """
        Move the cursor to a specific position
        Both x and y must be within the boundary
        :param x:
        :param y:
        :return:
        """
        if x >= self.max_x:
            x = self.max_x - 1
        if y >= self.max_y:
            y = self.max_y - 1
        self.terminal_screen.move(y, x)

    def move_shift_right(self):
        if self.shifted < 1000:
            self.shifted += 1

    def move_shift_left(self):
        if self.shifted > 0:
            self.shifted -= 1

    def shift_string(self, text, max_x=None):
        """
        to support string too long, the text can be shifted
        this function shifts and cuts the string to show only a part of this
        :param max_x:
        :param text:
        :return:
        """
        if max_x is None:
            max_x = self.max_x

        text = text[self.shifted:]
        text_len = len(text)
        if text_len <= max_x:
            return text
        else:
            return text[:max_x - 2] + self._TEXT_TO_LONG

    def set_x(self, x):
        self.x = x

    def set_y(self, y, x=0):
        self.x = x
        self.y = y

    def new_line(self, x=0):
        self.y += 1
        self.x = x

    def get_max_x(self):
        return self.max_x

    def get_max_y(self):
        return self.max_y

    def draw_row(self, text, x=None, x_indent=0, color=1):
        """
        draw data to console and take care to not exceed borders
        :param text:
        :param x:
        :param x_indent:
        :param color:
        :return:
        """
        # if x is defined use it as absolute x
        if x is None:
            self.x += x_indent
        else:
            self.x = x

        # check if we can print this line
        if self.y < self.max_y:
            # check if text to print is too long
            text_len = len(text)
            # if empty text
            if text_len == 0:
                return
            # if no space left
            elif self.max_x - self.x <= 0:
                self.terminal_screen.addstr(self.y, self.max_x - len(self._TEXT_TO_LONG) - 1, self._TEXT_TO_LONG, color)
            # enough space for text
            elif self.max_x - self.x - text_len > 0:
                self.terminal_screen.addstr(self.y, self.x, str(text), color)
                self.x += text_len
            # start draw from the beginning of the line and draw for the entire line
            elif self.x == 0 and self.max_x - text_len == 0:
                # note: this is a corner case of the previous case but
                #       because of a strange behavior of the 'addstr' method (maybe a bug)
                #       we cannot draw a string which could perfectly fit in the remaining space if
                #       the start point (x) is different from 0
                #       example: before   [sample string      ]
                #                after    [sample string value] -> crash
                #       but:     before   [                   ]
                #                after    [one single big line] -> that ok
                self.terminal_screen.addstr(self.y, self.x, str(text), color)
                self.x += text_len
            else:
                # cut part of text longer than max
                cut_text = text[:(self.max_x - self.x - 1)]
                self.terminal_screen.addstr(self.y, self.x, str(cut_text), color)
                self.x += len(cut_text)
                self.terminal_screen.addstr(self.y, self.max_x - len(self._TEXT_TO_LONG) - 1, self._TEXT_TO_LONG, color)
                self.x += len(self._TEXT_TO_LONG)


