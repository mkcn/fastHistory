# -*-coding:utf-8-*-

import curses
import logging

from parser.bashParser import BashParser
from database.dataManager import DataManager
from pick.drawer import Drawer
from pick.pageSelect import PageSelector

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_DELETE = curses.KEY_BACKSPACE
KEY_CANC = curses.KEY_DC
KEY_TAB = 9
KEY_ESC = 27  # NOTE: the KEY_ESC can be received with some delay
KEY_TAG = 35
KEY_AT = 64
KEY_SHIFT_TAB = curses.KEY_BTAB
KEY_RIGHT = curses.KEY_RIGHT
KEY_LEFT = curses.KEY_LEFT
KEY_RESIZE = curses.KEY_RESIZE
KEY_SELECT = None  # TODO decide


class Picker(object):
    """
    Class used to show the available value and select one (or more)
    """

    SMART_HISTORY_TITLE = "Smart History search"
    DESCRIPTION_CONTEXT_LENGTH = 5

    DEBUG_MODE = True

    def __init__(self, data_manager, search_text="", multi_select=False):
        """
        initialize variables and get filtered list starting options to show
        :param data_manager          the data manager object to retrieve data
        :param search_text:         (optional) if defined the results will be filtered with this text, default emtpy string
        :param multi_select:        (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
        """

        self.search_text = search_text
        self.search_text_lower = search_text.lower()
        self.data_manager = data_manager
        self.all_selected = []

        self.drawer = None
        self.flags_for_info_cmd = None

        self.is_multi_select = multi_select

        self.cmd_meaning = None
        self.cmd_flag1 = None

        # object to handle the page selector
        self.page_selector = None

        self.index = 0
        self.current_line_index = 0
        self.options = None
        self.option_to_draw = None

        self.current_selected_option = None

    def has_minimum_size(self):
        """
        # draw screen if screen has minimum size
        :return:    true if the console has at least the minimum size
        """
        return self.drawer.get_max_y() < 4 or self.drawer.get_max_x() < 40

    def draw_edit_description(self):
        """
        controller of description page drawer
        :return:
        """
        if self.has_minimum_size():
            return
        self.drawer.clear()
        self.drawer.reset()

        # import this locally to improve performance when the program is loaded
        from pick.pageEditDescription import PageEditDescription
        page_tags = PageEditDescription(self.drawer, self.page_selector)
        page_tags.draw_page(option=self.current_selected_option, search_text_lower=self.search_text_lower)

        # refresh screen
        self.drawer.refresh()

    def draw_edit_tags(self):
        """
        controller of tags page drawer
        :return:
        """
        if self.has_minimum_size():
            return
        self.drawer.clear()
        self.drawer.reset()

        # import this locally to improve performance when the program is loaded
        from pick.pageEditTags import PageEditTags
        page_tags = PageEditTags(self.drawer, self.page_selector)
        page_tags.draw_page(option=self.current_selected_option, search_text_lower=self.search_text_lower)

        # refresh screen
        self.drawer.refresh()

    def draw_info(self):
        """
        controller of info page drawer
        :return:
        """
        if self.has_minimum_size():
            return
        self.drawer.clear()
        self.drawer.reset()

        # import this locally to improve performance when the program is loaded
        from pick.pageInfo import PageInfo
        page_info = PageInfo(self.drawer, self.page_selector)
        page_info.draw_page_info(option=self.current_selected_option,
                                 search_text_lower=self.search_text_lower,
                                 flags_for_info_cmd=self.flags_for_info_cmd)

        # refresh screen
        self.drawer.refresh()

    def draw_select(self):
        """
        controller of select page drawer
        :return:
        """
        if self.has_minimum_size():
            return
        self.drawer.clear()
        self.drawer.reset()

        smart_options = self.get_smart_options()
        self.page_selector.draw_page_select(
            search_text_lower=self.search_text_lower,
            title=self.SMART_HISTORY_TITLE,
            search_text=self.search_text,
            smart_options=smart_options)

        # refresh screen
        self.drawer.refresh()

    def move_up(self):
        """
        if it is not already on the first line move up
        :return:
        """
        if self.index > 0:
            self.index -= 1
            number_option_to_draw = self.drawer.get_max_y() - 3
            # the current line is the first line
            if self.current_line_index == 0:
                self.option_to_draw = self.options[self.index:self.index+number_option_to_draw]
            else:
                self.current_line_index -= 1

    def move_down(self):
        """
        if it is not already on the last line move down
        :return:
        """
        if self.index + 1 < len(self.options):
            self.index += 1
            number_option_to_draw = self.drawer.get_max_y() - 3
            # the current line is the last line
            # current line starts from 0
            if self.current_line_index == number_option_to_draw - 1:
                # array   [0,1,2,3,4,5]
                #            |   |
                # pointer        *
                # start   3(pointer)-3(n option to draw) + 1 = 1
                # end     3(pointer) + 1  = 4
                # result  [1,2,3]
                self.option_to_draw = self.options[self.index + 1 - number_option_to_draw:self.index + 1]
            else:
                self.current_line_index += 1

    def get_number_options_to_draw(self):
        """
        get total number of options which can be drawn
        this is calculated as the max y - 3: 1 for the title, 1 for the column title and 1 for the last info line
        :return:
        """
        return self.drawer.get_max_y() - 3

    def update_options_to_draw(self, initialize_index=False):
        """
        update the variable "option to draw" based on the size of the screen
        :type initialize_index:     True to reset index to the first option
        :return:
        """
        number_option_to_draw = self.get_number_options_to_draw()
        if initialize_index:
            self.index = 0
            self.current_line_index = 0
        else:
            # check if the current selected line is too big set the last line as selected line
            if self.current_line_index >= number_option_to_draw:
                self.index -= self.current_line_index - number_option_to_draw + 1
                self.current_line_index = number_option_to_draw - 1

        # option            a,b,c,d,e,f
        # option_i          0,1,2,3,4,5
        # index             \-----*
        # windows               0,1,2
        # current_line          \-*
        # wanted result         c,d,e
        #
        # start point       = 3 - 1 = 2
        # end point         = 2 + 3 + 1
        # result            = [a,b,c,d,e,f][3:5] = [c,d,e]
        self.option_to_draw = self.options[
                              self.index - self.current_line_index:
                              self.index - self.current_line_index + number_option_to_draw]

    def initialize_options_to_draw(self):
        """
        initialize the variable "option to draw" based on the size of the screen

        :return:
        """
        number_option_to_draw = self.get_number_options_to_draw()
        self.option_to_draw = self.options[0:number_option_to_draw]

    def mark_index(self):
        """
        method not used yet to support multi selection
        :return:
        """
        if self.is_multi_select:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)

    def get_selected(self):
        """
        return the current selected option as a tuple: (option, index)
        or as a list of tuples (in case multi_select==True)
        """
        if self.is_multi_select:
            return_tuples = []
            for selected in self.all_selected:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            # if not option available return an emtpy response
            if len(self.options) == 0:
                return ["", [], None], -1
            return self.options[self.index], self.index

    def get_smart_options(self):
        """
        get list of options to show
        :return:
        """
        options = []
        for row_index, option in enumerate(self.option_to_draw):
            if row_index == self.current_line_index:
                options.append([True, option])
                self.current_selected_option = option
            else:
                options.append([False, option])
        return options

    def run_loop_edit_description(self):
        """
        Loop to capture user input keys to interact with the "add description" page

        :return:
        """
        while True:
            self.draw_edit_description()
            # wait for char
            c = self.drawer.wait_next_char()

            # save and exit
            if c in KEYS_ENTER:
                return
            # exit without saving
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return None
            # -> command
            elif c == KEY_RIGHT:
                self.drawer.move_shift_right()
            # <- command
            elif c == KEY_LEFT:
                self.drawer.move_shift_left()
            else:
                logging.error("char not handled: " + str(c))

    def run_loop_edit_tags(self):
        """
        Loop to capture user input keys to interact with the "add tag" page

        :return:
        """
        while True:
            self.draw_edit_tags()
            # wait for char
            c = self.drawer.wait_next_char()

            # save and exit
            if c in KEYS_ENTER:
                return
            # exit without saving
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return None
            # -> command
            elif c == KEY_RIGHT:
                self.drawer.move_shift_right()
            # <- command
            elif c == KEY_LEFT:
                self.drawer.move_shift_left()
            else:
                logging.error("char not handled: " + str(c))

    def run_loop_info(self):
        """
        Loop to capture user input keys to interact with the info page

        :return:
        """
        self.flags_for_info_cmd = BashParser.load_data_for_info_cmd(
            cmd_text=self.current_selected_option[DataManager.INDEX_OPTION_CMD])

        while True:
            self.draw_info()
            # wait for char
            c = self.drawer.wait_next_char()

            # select current entry
            if c in KEYS_ENTER:
                return self.get_selected()
            # delete selected entry
            elif c == KEY_CANC:
                # TODO implement delete entry
                logging.info("TODO delete selected entry")
                pass
            # go back to select page
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return None
            # -> command
            elif c == KEY_RIGHT:
                self.drawer.move_shift_right()
            # <- command
            elif c == KEY_LEFT:
                self.drawer.move_shift_left()
            # normal search char
            elif c == KEY_TAG:  # "#"
                self.run_loop_edit_tags()
            # delete a char of the search
            elif c == KEY_AT:  # "@"
                self.run_loop_edit_description()
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                # TODO make this more efficient
                # update list option
                self.options = self.data_manager.filter(self.search_text_lower,
                                                        self.index + self.get_number_options_to_draw())
                # update the options to show
                self.update_options_to_draw()
            else:
                logging.error("char not handled: " + str(c))

    def run_loop_select(self):
        """
        Loop to capture user input keys to interact with the select page

        """
        # get filtered starting options
        self.options = self.data_manager.filter(self.search_text_lower, self.get_number_options_to_draw())
        self.initialize_options_to_draw()

        while True:
            self.draw_select()
            # wait for char
            c = self.drawer.wait_next_char()

            # check char and execute command
            if c == KEY_UP:
                self.move_up()
            elif c == KEY_DOWN:
                self.move_down()
                # retrieve more data from db when user want to view more
                if self.index % (self.get_number_options_to_draw() - 1) == 0:
                    self.options = self.data_manager.filter(
                        self.search_text_lower,
                        self.index + self.get_number_options_to_draw())
            elif c in KEYS_ENTER:
                return self.get_selected()
            elif c == KEY_SELECT and self.is_multi_select:
                self.mark_index()
            # tab command
            elif c == KEY_TAB:
                res = self.run_loop_info()
                if res is not None:
                    return res
            # -> command
            elif c == KEY_RIGHT:
                self.drawer.move_shift_right()
            # <- command
            elif c == KEY_LEFT:
                self.drawer.move_shift_left()
            # normal search char
            elif c in range(256):
                self.search_text += chr(c)
                self.search_text_lower += chr(c).lower()
                self.option_to_draw = None
                self.options = self.data_manager.filter(self.search_text_lower, self.get_number_options_to_draw())
                # update the options to show
                self.update_options_to_draw(initialize_index=True)
            # delete a char of the search
            elif c == KEY_DELETE:
                if len(self.search_text) > 0:
                    self.search_text = self.search_text[:-1]
                    self.search_text_lower = self.search_text_lower[:-1]
                    self.options = self.data_manager.filter(self.search_text_lower, self.get_number_options_to_draw())
                    # update the options to show
                    self.update_options_to_draw(initialize_index=True)
            elif c == KEY_CANC:
                # TODO implement delete entry
                logging.info("TODO delete selected entry")
                pass
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                # TODO make this more efficient
                # update list option
                self.options = self.data_manager.filter(self.search_text_lower, self.index + self.get_number_options_to_draw())
                # update the options to show
                self.update_options_to_draw()
            else:
                logging.error("char not handled: " + str(c))

    def _start(self, screen):
        self.drawer = Drawer(screen)
        self.page_selector = PageSelector(self.drawer)

        return self.run_loop_select()

    def start(self):
        return curses.wrapper(self._start)

