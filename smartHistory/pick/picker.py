# -*-coding:utf-8-*-

import curses
import logging

from parser import bashlex
from parser.bashParser import BashParser
from parser.manParser import ManParser
from database.dataRetriever import DataRetriever
from pick.drawer import Drawer
from pick.pageSelect import PageSelector

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = curses.KEY_UP
KEYS_DOWN = curses.KEY_DOWN
KEYS_DELETE = (curses.KEY_BACKSPACE, curses.KEY_DC)
KEYS_TAB = 9
KEY_ESC = 27  # NOTE: the KEY_ESC can be received with some delay
KEYS_GO_BACK = (curses.KEY_BTAB, KEY_ESC)
KEY_RIGHT = curses.KEY_RIGHT
KEY_LEFT = curses.KEY_LEFT
KEY_RESIZE = curses.KEY_RESIZE
KEYS_SELECT = None  # TODO decide


class Picker(object):
    """
    Class used to show the available value and select one (or more)
    """

    SMART_HISTORY_TITLE = "Smart History search"
    DESCRIPTION_CONTEXT_LENGTH = 5

    DEBUG_MODE = True

    def __init__(self, search_text="", multi_select=False):
        """
        initialize variables and get filtered list starting options to show
        :param search_text:         (optional) if defined the results will be filtered with this text, default emtpy string
        :param multi_select:        (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
        """

        self.search_text = search_text
        self.search_text_lower = search_text.lower()
        self.data_retriever = DataRetriever()
        self.all_selected = []

        self.drawer = None
        self.flags_for_info_cmd = None

        # bool to change the context to the info page
        self.is_info_page_shown = False

        self.is_multi_select = multi_select

        self.cmd_meaning = None
        self.cmd_flag1 = None

        # object to handle the page selector
        self.page_selector = None

        self.index = 0
        self.current_line_index = 0
        self.option_to_draw = None

        self.current_selected_option = None

        # get filtered starting options
        self.options = self.data_retriever.filter(self.search_text_lower)

    def draw_smart(self):
        """
        main controller of page drawer
        :return:
        """
        # clear screen
        self.drawer.clear()
        # reset terminal
        self.drawer.reset()

        if self.is_info_page_shown:
            # import this locally to improve performance when the program is loaded
            from pick.pageInfo import PageInfo
            page_info = PageInfo(self.drawer, self.page_selector)
            page_info.draw_page_info(option=self.current_selected_option,
                                     search_text_lower=self.search_text_lower,
                                     flags_for_info_cmd=self.flags_for_info_cmd)
        else:
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
        logging.debug("self.index " + str(self.index))
        if self.index > 0:
            self.index -= 1
            number_option_to_draw = self.drawer.get_max_y() - 3
            # the current line is the first line
            if self.current_line_index == 0:
                self.option_to_draw = self.options[self.index:self.index+number_option_to_draw]
                logging.debug("self.index: " + str(self.index))
                logging.debug("self.current_line: " + str(self.current_line_index))
                logging.debug("number_option_to_draw: " + str(number_option_to_draw))
                logging.debug("option_to_draw: " + str(len(self.option_to_draw)))
            else:
                self.current_line_index -= 1

    def move_down(self):
        """
        if it is not already on the last line move down
        :return:
        """
        logging.debug("self.index " + str(self.index))
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
                logging.debug("self.index: " + str(self.index))
                logging.debug("self.current_line: " + str(self.current_line_index))
                logging.debug("number_option_to_draw: " + str(number_option_to_draw))
                logging.debug("option_to_draw: " + str(len(self.option_to_draw)))
            else:
                logging.debug("current_line +1")
                self.current_line_index += 1
        else:
            logging.debug("index > len option")

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

    def load_data_for_info_cmd(self, cmd_text):
        """
        retrieve info about the currently selected cmd from the man page

        TODO move this method to different class
        :param cmd_text:    the bash cmd string
        :return:            a structured list with info for each cmd and flags
        """
        # here the man search and parse
        parser = BashParser()
        # create a result var to fill
        flags_for_info_cmd = list()
        # parse the cmd string
        cmd_parsed = bashlex.parse(cmd_text)
        # find all flags for each commands
        parser.get_flags_from_bash_node(cmd_parsed, flags_for_info_cmd)
        # for each cmd and flag find the meaning from the man page
        man_parsed = ManParser()
        for item in flags_for_info_cmd:
            cmd_main = item[BashParser.INDEX_CMD]
            cmd_flags = item[BashParser.INDEX_FLAGS]
            if man_parsed.load_man_page(cmd_main[BashParser.INDEX_VALUE]):
                # save cmd meaning
                cmd_main[BashParser.INDEX_MEANING] = man_parsed.get_cmd_meaning()
                # cmd meaning found in the man page
                if cmd_main[BashParser.INDEX_MEANING]:
                    cmd_flags_updated = list()
                    for flag_i in range(len(cmd_flags)):
                        flag = cmd_flags[flag_i]
                        flag[BashParser.INDEX_MEANING] = man_parsed.get_flag_meaning(flag[BashParser.INDEX_VALUE])
                        # if flag found in the man page
                        if flag[BashParser.INDEX_MEANING]:
                            cmd_flags_updated.append(flag)
                        else:
                            # try to check if flag is concatenated
                            conc_flags = BashParser.decompose_possible_concatenated_flags(flag[BashParser.INDEX_VALUE])
                            for conc_flag in conc_flags:
                                conc_flag_meaning = man_parsed.get_flag_meaning(conc_flag)
                                cmd_flags_updated.append([conc_flag, conc_flag_meaning])
                    # set the updated flags as new list of flags, the old list is deleted
                    item[BashParser.INDEX_FLAGS] = cmd_flags_updated
        return flags_for_info_cmd

    def run_loop(self):
        """
        Loop to capture user input keys
        """
        self.initialize_options_to_draw()

        while True:
            # draw screen if screen has minimum size
            if self.drawer.get_max_y() > 3 and self.drawer.get_max_x() > 40:
                self.draw_smart()
            # wait for char
            c = self.drawer.wait_next_char()

            if c == KEYS_UP:
                self.move_up()
            elif c == KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                return self.get_selected()
            elif c == KEYS_SELECT and self.is_multi_select:
                self.mark_index()
            # tab command
            elif c == KEYS_TAB:
                self.is_info_page_shown = True
                self.flags_for_info_cmd = self.load_data_for_info_cmd(
                    cmd_text=self.current_selected_option[DataRetriever.INDEX_OPTION_CMD])
            elif c in KEYS_GO_BACK:
                self.is_info_page_shown = False
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
                self.options = self.data_retriever.filter(self.search_text)
                # update the options to show
                self.update_options_to_draw(initialize_index=True)
            # delete a char of the search
            elif c in KEYS_DELETE:
                if len(self.search_text) > 0:
                    self.search_text = self.search_text[:-1]
                    self.search_text_lower = self.search_text_lower[:-1]
                    self.options = self.data_retriever.filter(self.search_text_lower)
                    # update the options to show
                    self.update_options_to_draw(initialize_index=True)
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                # update the options to show
                self.update_options_to_draw()
            else:
                logging.error("char not handled: " + str(c))

    def _start(self, screen):
        self.drawer = Drawer(screen)
        self.page_selector = PageSelector(self.drawer)
        return self.run_loop()

    def start(self):
        return curses.wrapper(self._start)

