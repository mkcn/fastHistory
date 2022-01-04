import curses

from fastHistory.config.configReader import ConfigReader


class Drawer(object):
    """
    Class to handle the console drawer
    """

    NULL_COLOR = 0

    def __init__(self, screen, theme, text_too_long):
        self.terminal_screen = screen
        self.max_y, self.max_x = self.terminal_screen.getmaxyx()
        self.x = 0
        self.y = 0
        self.text_too_long = text_too_long
        self.input_timeout_enabled = False

        # define colors
        self.color_search_input = None
        self.color_search = None
        self.color_hash_tag = None
        self.color_hash_tag_disable = None
        self.color_hash_tag_selected = None
        self.color_tab_focus = None
        self.color_tab_no_focus = None
        self.color_cmd_sample = None
        self.color_selected_row = None
        self.color_selected_row_no_focus = None
        self.color_selector = None
        self.color_columns_title = None
        self.init_colors(theme)

        from sys import platform
        self.is_mac_os = (platform == "darwin")

    def init_colors(self, theme):
        """
        define and set console colors
        :return:
        """
        # use the default colors of the terminal
        curses.use_default_colors()

        id_color_green_on_white = 1
        id_color_black_on_white = 2
        id_color_black_on_green = 3
        id_color_green_on_black = 4
        id_color_cyan_on_white = 5
        id_color_white_on_black = 6
        id_color_white_on_cyan = 7
        id_color_white_on_green = 8
        id_color_cyan = 9
        id_color_green = 10
        id_color_black = 11

        curses.init_pair(id_color_black, curses.COLOR_BLACK, -1)
        self.color_hash_tag_disable = curses.color_pair(id_color_black) | curses.A_BOLD
        # set colors
        if theme == ConfigReader.THEME_AZURE:
            curses.init_pair(id_color_cyan, curses.COLOR_CYAN, -1)
            curses.init_pair(id_color_green_on_white, curses.COLOR_GREEN, curses.COLOR_WHITE)
            curses.init_pair(id_color_black_on_white, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(id_color_white_on_cyan, curses.COLOR_WHITE, curses.COLOR_CYAN)
            curses.init_pair(id_color_cyan_on_white, curses.COLOR_CYAN, curses.COLOR_WHITE)

            self.color_search_input = curses.color_pair(id_color_cyan) | curses.A_BOLD
            self.color_cmd_sample = curses.color_pair(id_color_cyan)
            self.color_hash_tag = curses.color_pair(id_color_cyan)
            self.color_tab_no_focus = curses.color_pair(id_color_black_on_white)
            self.color_selected_row = curses.color_pair(id_color_black_on_white) | curses.A_BOLD
            self.color_selected_row_no_focus = curses.color_pair(id_color_white_on_cyan) | curses.A_BOLD
            self.color_search = curses.color_pair(id_color_white_on_cyan) | curses.A_BOLD
            self.color_hash_tag_selected = curses.color_pair(id_color_cyan_on_white)
            self.color_selector = curses.color_pair(id_color_black_on_white)
            self.color_columns_title = curses.color_pair(id_color_white_on_cyan) | curses.A_BOLD
        else:
            curses.init_pair(id_color_green_on_black, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(id_color_white_on_black, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(id_color_black_on_white, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(id_color_black_on_green, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(id_color_white_on_green, curses.COLOR_WHITE, curses.COLOR_GREEN)
            curses.init_pair(id_color_green, curses.COLOR_GREEN, -1)

            self.color_search_input = curses.color_pair(id_color_green) | curses.A_BOLD
            self.color_cmd_sample = curses.color_pair(id_color_green)
            self.color_hash_tag = curses.color_pair(id_color_green) | curses.A_BOLD
            self.color_tab_no_focus = curses.color_pair(id_color_green_on_black)
            self.color_selected_row = curses.color_pair(id_color_white_on_black) | curses.A_BOLD
            self.color_selected_row_no_focus = curses.color_pair(id_color_white_on_green) | curses.A_BOLD
            self.color_search = curses.color_pair(id_color_white_on_green) | curses.A_BOLD
            self.color_hash_tag_selected = curses.color_pair(id_color_green_on_black) | curses.A_BOLD
            self.color_selector = curses.color_pair(id_color_green_on_black)
            self.color_columns_title = curses.color_pair(id_color_black_on_green) | curses.A_BOLD
        self.color_tab_focus = self.color_columns_title

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

    def wait_next_char(self, multi_threading_mode=False):
        """
        wait input from user

        :param multi_threading_mode:      enabled or disabled the timeout to make the get_wch compatible with multi threading

        if the timeout is enabled and no input is received -> curses.error
        :return:
        """
        if multi_threading_mode:
            self._enable_input_timeout()
        elif not multi_threading_mode:
            self._disable_input_timeout()

        try:
            # get_wch supports wide characters
            c = self.terminal_screen.get_wch()
        except curses.error:
            if not self.is_mac_os:
                return curses.ERR
            else:
                # on macOS the resize key does not work as expected
                # as a workaround we send the resize key when the get_wch throws an error
                return curses.KEY_RESIZE
        except ValueError:
            return curses.ERR
        return c

    def _enable_input_timeout(self):
        """
        halfdelay set a timeout for get_wch
        this allows to have not blocking UI that works with threads
        """
        if not self.input_timeout_enabled:
            curses.halfdelay(1)  # 100 ms
            self.input_timeout_enabled = True

    def _disable_input_timeout(self):
        """
        reset halfdelay
        """
        if self.input_timeout_enabled:
            curses.cbreak()
            self.input_timeout_enabled = False

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

    def set_x(self, x):
        self.x = x

    def set_y(self, y, x=0):
        self.x = x
        self.y = y

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def new_line(self, x=0):
        self.y += 1
        self.x = x

    def get_max_x(self):
        return self.max_x

    def get_max_y(self):
        return self.max_y

    def fill_row(self, char=" ", x=None, max_x=None, color=1):
        if x is not None:
            self.x = x
        if max_x is None:
            max_x = self.max_x

        if max_x - self.x >= 0:
            text_len = max_x - self.x
            text = char[0] * text_len
            self.terminal_screen.addstr(self.y, self.x, str(text), color)
            self.x += text_len

    def draw_row(self, text, x=None, x_indent=0, color=1, allow_last_row=False, return_unprinted=False):
        """
        draw data to console and take care to not exceed borders
        :param text:
        :param x:
        :param x_indent:
        :param color:
        :param allow_last_row:
        :param return_unprinted:
        :return:
        """
        empty_str = ""
        # if x is defined use it as absolute x
        if x is None:
            self.x += x_indent
        else:
            self.x = x

        if allow_last_row:
            margin_bottom = 0
        else:
            margin_bottom = 1

        # check if we can print this line
        if self.y < self.max_y - margin_bottom:
            # check if text to print is too long
            text_len = len(text)
            # if empty text
            if text_len == 0:
                return empty_str
            # if no space left
            elif self.max_x - self.x <= 0:
                self.terminal_screen.addstr(self.y, self.max_x - len(self.text_too_long) - 1, self.text_too_long, color)
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
                cut_index = (self.max_x - self.x - 1)
                cut_text = text[:cut_index]
                self.terminal_screen.addstr(self.y, self.x, str(cut_text), color)
                self.x += len(cut_text)
                if return_unprinted:
                    # return the unprinted string
                    return text[cut_index:]
                else:
                    self.terminal_screen.addstr(self.y, self.max_x - len(self.text_too_long) - 1, self.text_too_long, color)
                    self.x += len(self.text_too_long)
        return empty_str


