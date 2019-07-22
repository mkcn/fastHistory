# -*-coding:utf-8-*-

import curses
import logging

from parser.bashParser import BashParser
from database.dataManager import DataManager
from parser.inputParser import InputParser
from pick.drawer import Drawer
from pick.pageSelect import PageSelector
from pick.textManager import TextManager, ContextShifter

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
KEY_CTRL_SPACE = '\x00'
KEY_START = curses.KEY_HOME
KEY_END = curses.KEY_END
KEYS_EDIT = ('e', 'E')
KEY_TAG = '#'
KEY_AT = '@'


class Picker(object):
    """
    Class used to show the available value and select one (or more)
    """

    DESCRIPTION_CONTEXT_LENGTH = 5
    EDIT_FIELD_MARGIN = 4
    SEARCH_FIELD_MARGIN = 23

    DEBUG_MODE = True

    def __init__(self, data_manager, theme, last_column_size, search_text="", multi_select=False):
        """
        initialize variables and get filtered list starting options to show
        :param data_manager          the data manager object to retrieve data
        :param search_text:         (optional) if defined the results will be filtered with this text, default emtpy string
        :param multi_select:        (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
        """

        self.context_shift = ContextShifter()
        self.search_t = TextManager(search_text, use_lower=True)

        self.data_manager = data_manager
        self.theme = theme
        self.last_column_size = last_column_size
        self.all_selected = []

        self.drawer = None

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

    def start(self):
        """
        starting point
        :return:
        """
        return curses.wrapper(self._start)

    def _start(self, screen):
        self.drawer = Drawer(screen, self.theme, TextManager.TEXT_TOO_LONG)
        self.page_selector = PageSelector(self.drawer)

        # set screen context
        self.search_t.set_max_x(self.drawer.get_max_x() - self.SEARCH_FIELD_MARGIN)

        return self.run_loop_select

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
            # this is needed for the console resize event
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
        :return: the current selected option as a tuple: (option, index) or as a list of tuples (if multi_select==True)
        """
        if self.is_multi_select:
            return_tuples = []
            for selected in self.all_selected:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            # if not option available return an emtpy response
            option_count = len(self.options)
            if option_count == 0 or self.index >= option_count or self.index < 0:
                return ""
            selected_cmd = self.options[self.index][DataManager.OPTION.INDEX_CMD]
            # update order of the selected cmd
            self.data_manager.update_element_order(selected_cmd)
            return selected_cmd

    def get_options(self):
        """
        TODO split this function into:
            - get_options()
            - update_current_selected_option()
        :return: list of options to show
        """
        tmp_options = []
        for row_index, option in enumerate(self.option_to_draw):
            if row_index == self.current_line_index:
                tmp_options.append([True, option])
                self.current_selected_option = option
            else:
                tmp_options.append([False, option])
        return tmp_options

    def run_loop_edit_command(self,blocks_shift, data_from_man_page):
        """
        loop to capture user input keys to interact with the "edit command" page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from pick.pageEditCommand import PageEditCommand
        page_desc = PageEditCommand(self.drawer,
                                    option=self.current_selected_option,
                                    search_filters=self.data_manager.get_search_filters(),
                                    context_shift=self.context_shift,
                                    blocks_shift=blocks_shift,
                                    data_from_man_page=data_from_man_page)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        command_t = TextManager(self.current_selected_option[DataManager.OPTION.INDEX_CMD],
                                max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        input_error_msg = None

        while True:
            if page_desc.has_minimum_size():
                page_desc.clean_page()
                page_desc.draw_page_edit(command_text=command_t.get_text_to_print(),
                                         command_cursor_index=command_t.get_cursor_index_to_print(),
                                         input_error_msg=input_error_msg)
                page_desc.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char()

            # save and exit
            if c in KEYS_ENTER:
                if current_command == command_t.get_text():
                    return False
                else:
                    is_valid_command = InputParser.is_cmd_str_valid(command_t.get_text())
                    if is_valid_command:
                        if self.data_manager.update_command(current_command, command_t.get_text()):
                            # if an other item exists with the new command text, it is
                            # deleted and merged with the old command item by the db function.
                            # In this case the GUI index must be correctly adjusted (this is needed only if
                            # the delete item was before the updated one in the options array)
                            for option in self.options:
                                if option[DataManager.OPTION.INDEX_CMD] == command_t.get_text():
                                    self.move_up()
                                    break
                                if option[DataManager.OPTION.INDEX_CMD] == current_command:
                                    break
                            return True
                        else:
                            msg = "database error during saving, please try again"
                            logging.error(msg)
                            input_error_msg = msg
                    else:
                        msg = "no tags and description are allowed here"
                        logging.error(msg + ": " + str(command_t.get_text()))
                        input_error_msg = msg

            # exit without saving
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return False
            # -> command
            elif c == KEY_RIGHT:
                if command_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    command_t.move_cursor_right()
                # <- command
            elif c == KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not command_t.is_cursor_at_the_beginning():
                    command_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in KEYS_DELETE:
                command_t.delete_char()
                input_error_msg = None
            # move cursor to the beginning
            elif c == KEY_START or c == KEY_CTRL_A:
                command_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == KEY_END or c == KEY_CTRL_E:
                command_t.move_cursor_to_end()
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                command_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif type(c) is str:
                # TODO check input max len
                command_t.add_string(c, self.data_manager.get_forbidden_chars())
                input_error_msg = None
            elif type(c) is int:
                logging.debug("loop edit command - integer input not handled: " + repr(c))
            else:
                logging.error("loop edit command - input not handled: " + repr(c))

    def run_loop_edit_description(self, blocks_shift, data_from_man_page):
        """
        loop to capture user input keys to interact with the "add description" page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from pick.pageEditDescription import PageEditDescription
        page_desc = PageEditDescription(self.drawer,
                                        option=self.current_selected_option,
                                        search_filters=self.data_manager.get_search_filters(),
                                        context_shift=self.context_shift,
                                        blocks_shift=blocks_shift,
                                        data_from_man_page=data_from_man_page)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        description_t = TextManager(InputParser.DESCRIPTION_SIGN +
                                    self.current_selected_option[DataManager.OPTION.INDEX_DESC],
                                    max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        input_error_msg = None

        while True:
            if page_desc.has_minimum_size():
                page_desc.clean_page()
                page_desc.draw_page_edit(description_text=description_t.get_text_to_print(),
                                         description_cursor_index=description_t.get_cursor_index_to_print(),
                                         input_error_msg=input_error_msg)
                page_desc.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char()

            # save and exit
            if c in KEYS_ENTER:
                new_description = InputParser.parse_description(description_t.get_text())
                if new_description is not None:
                    if self.data_manager.update_description(current_command, new_description):
                        return True
                    else:
                        msg = "database error during saving, please try again"
                        logging.error(msg)
                        input_error_msg = msg
                else:
                    msg = "new description text not allowed"
                    logging.error(msg + ": " + str(description_t.get_text()))
                    input_error_msg = msg

            # exit without saving
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return False
            # -> command
            elif c == KEY_RIGHT:
                if description_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    description_t.move_cursor_right()
                # <- command
            elif c == KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not description_t.is_cursor_at_the_beginning():
                    description_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in KEYS_DELETE:
                description_t.delete_char()
                input_error_msg = None
            # move cursor to the beginning
            elif c == KEY_START or c == KEY_CTRL_A:
                description_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == KEY_END or c == KEY_CTRL_E:
                description_t.move_cursor_to_end()
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                description_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif type(c) is str:
                # TODO check input max len
                description_t.add_string(c, self.data_manager.get_forbidden_chars())
                input_error_msg = None
            elif type(c) is int:
                logging.debug("loop edit description - integer input not handled: " + repr(c))
            else:
                logging.error("loop edit description - input not handled: " + repr(c))

    def run_loop_edit_tags(self, data_from_man_page):
        """
        loop to capture user input keys to interact with the "add tag" page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from pick.pageEditTags import PageEditTags
        page_tags = PageEditTags(self.drawer,
                                 option=self.current_selected_option,
                                 search_filters=self.data_manager.get_search_filters(),
                                 context_shift=self.context_shift,
                                 data_from_man_page=data_from_man_page)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        new_tags = self.current_selected_option[DataManager.OPTION.INDEX_TAGS]
        new_tags_str = ""
        for tag in new_tags:
            if len(tag) > 0:
                new_tags_str += InputParser.TAG_SIGN + tag + " "

        new_tags_t = TextManager(new_tags_str, max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        new_tags_t.add_string(InputParser.TAG_SIGN, self.data_manager.get_forbidden_chars())

        input_error_msg = None

        while True:
            if page_tags.has_minimum_size():
                page_tags.clean_page()
                page_tags.draw_page_edit(tags_text=new_tags_t.get_text_to_print(),
                                         tags_cursor_index=new_tags_t.get_cursor_index_to_print(),
                                         input_error_msg=input_error_msg)
                page_tags.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char()

            # save and exit
            if c in KEYS_ENTER:
                new_tags_array = InputParser.parse_tags_str(new_tags_t.get_text())
                if new_tags_array is not None:
                    if self.data_manager.update_tags(current_command, new_tags_array):
                        return True
                    else:
                        msg = "database error during saving, please try again"
                        logging.error(msg)
                        input_error_msg = msg
                else:
                    msg = "new tags text is not allowed"
                    logging.error(msg + ": " + str(new_tags_t.get_text()))
                    input_error_msg = msg
            # exit without saving
            # TODO fix return if "alt+char" is pressed
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return False
            # -> command
            elif c == KEY_RIGHT:
                if new_tags_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    # move the search cursor one position right (->)
                    new_tags_t.move_cursor_right()
                # <- command
            elif c == KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not new_tags_t.is_cursor_at_the_beginning():
                    new_tags_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
                    # delete a char of the search
            elif c in KEYS_DELETE:
                # the delete is allowed if the search text is not empty and if
                if new_tags_t.delete_char():
                    self.context_shift.reset_context_shifted()
                input_error_msg = None
            # move cursor to the beginning
            elif c == KEY_START or c == KEY_CTRL_A:
                new_tags_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == KEY_END or c == KEY_CTRL_E:
                new_tags_t.move_cursor_to_end()
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                new_tags_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif type(c) is str:
                new_tags_t.add_string(c, self.data_manager.get_forbidden_chars())
                input_error_msg = None
            elif type(c) is int:
                logging.debug("loop edit tag - integer input not handled: " + repr(c))
            else:
                logging.error("loop edit tag - input not handled: " + repr(c))

    def run_loop_info(self):
        """
        Loop to capture user input keys to interact with the info page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from pick.pageInfo import PageInfo

        data_from_man_page = BashParser.load_data_for_info_from_man_page(
            cmd_text=self.current_selected_option[DataManager.OPTION.INDEX_CMD])
        page_info = PageInfo(self.drawer,
                             option=self.current_selected_option,
                             search_filters=self.data_manager.get_search_filters(),
                             context_shift=self.context_shift,
                             data_from_man_page=data_from_man_page)

        while True:
            if page_info.has_minimum_size():
                page_info.clean_page()
                page_info.draw_page()
                self.page_selector.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char()

            # select current entry
            if c in KEYS_ENTER:
                return self.get_selected()
            # delete current selected option
            elif c == KEY_CANC:
                self.data_manager.delete_element(self.current_selected_option[DataManager.OPTION.INDEX_CMD])
                self.options = self.data_manager.filter(self.search_t.get_text_lower(),
                                                        self.index + self.get_number_options_to_draw())
                self.update_options_to_draw()
                return None
            # go back to select page
            elif c == KEY_TAB or c == KEY_SHIFT_TAB or c == KEY_ESC:
                return None
            # open man page
            elif c == 109:  # char 'm'
                # TODO fix and show description in help line
                from console import consoleUtils
                cmd = data_from_man_page[0][BashParser.INDEX_CMD][BashParser.INDEX_VALUE]
                consoleUtils.ConsoleUtils.open_interactive_man_page(cmd)
                return ""
            # -> command
            elif c == KEY_RIGHT:
                self.context_shift.shift_context_right()
            # <- command
            elif c == KEY_LEFT:
                self.context_shift.shift_context_left()
            elif c == KEY_DOWN:
                page_info.shift_blocks_down()
            elif c == KEY_UP:
                page_info.shift_blocks_up()
            elif c in KEYS_EDIT:
                if self.run_loop_edit_command(page_info.get_blocks_shift(), data_from_man_page):
                    # reload options from db
                    self.options = self.data_manager.filter(self.search_t.get_text_lower(),
                                                            self.index + self.get_number_options_to_draw())
                    self.update_options_to_draw()
                    # update current selected option (based on an index)
                    self.get_options()  # TODO check if needed
                    # update option to show
                    page_info.update_option_value(self.current_selected_option)
                    # reload man page
                    data_from_man_page = BashParser.load_data_for_info_from_man_page(
                        self.current_selected_option[DataManager.OPTION.INDEX_CMD])
                    page_info.update_man_page(data_from_man_page)
            elif c == KEY_TAG:  # "#"
                if self.run_loop_edit_tags(data_from_man_page):
                    self.options = self.data_manager.filter(self.search_t.get_text_lower(),
                                                            self.index + self.get_number_options_to_draw())
                    self.update_options_to_draw()
                    self.get_options()
                    page_info.update_option_value(self.current_selected_option)
            elif c == KEY_AT:  # "@"
                if self.run_loop_edit_description(page_info.get_blocks_shift(), data_from_man_page):
                    self.options = self.data_manager.filter(self.search_t.get_text_lower(),
                                                            self.index + self.get_number_options_to_draw())
                    self.update_options_to_draw()
                    self.get_options()
                    page_info.update_option_value(self.current_selected_option)
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                self.search_t.set_max_x(self.drawer.get_max_x())
            else:
                logging.error("loop info - input not handled: " + repr(c))

    @property
    def run_loop_select(self):
        """
        Loop to capture user input keys to interact with the select page

        """
        # get filtered starting options
        self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.get_number_options_to_draw())
        self.initialize_options_to_draw()

        while True:
            if self.page_selector.has_minimum_size():
                self.page_selector.clean_page()
                self.page_selector.draw_page(
                    search_filters=self.data_manager.get_search_filters(),
                    options=self.get_options(),
                    search_t=self.search_t,
                    context_shift=self.context_shift,
                    last_column_size=self.last_column_size)
                self.page_selector.refresh_page()

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
                        self.search_t.get_text_lower(),
                        self.index + self.get_number_options_to_draw())
            elif c in KEYS_ENTER:
                return [True, self.get_selected()]
            elif c == KEY_CTRL_SPACE:
                return [False, self.get_selected()]
            # note: currently not implemented
            elif c == KEY_SELECT and self.is_multi_select:
                self.mark_index()
            # tab command
            elif c == KEY_TAB:
                # reset index of search text (to avoid confusion when the scroll is done on the info page)
                self.search_t.move_cursor_to_end()
                # call the loop for the info page
                res = self.run_loop_info()
                if res is not None:
                    # if return is not null then return selected result
                    return res
            # -> command
            elif c == KEY_RIGHT:
                if self.search_t.is_cursor_at_the_end():
                    if self.options != []:
                        # move all options list to right
                        self.context_shift.shift_context_right()
                else:
                    self.search_t.move_cursor_right()
            # <- command
            elif c == KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not self.search_t.is_cursor_at_the_beginning():
                    self.search_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in KEYS_DELETE:
                if self.search_t.delete_char():
                    # reset shift value
                    self.context_shift.reset_context_shifted()
                    self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.get_number_options_to_draw())
                    # update the options to show
                    self.update_options_to_draw(initialize_index=True)
            # delete current selected option
            elif c == KEY_CANC:
                self.data_manager.delete_element(self.current_selected_option[DataManager.OPTION.INDEX_CMD])
                self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.index + self.get_number_options_to_draw())
                self.update_options_to_draw()
            elif c == KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                self.search_t.set_max_x(self.drawer.get_max_x() - self.SEARCH_FIELD_MARGIN)
                # TODO make this more efficient
                # update list option
                self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.index + self.get_number_options_to_draw())
                # update the options to show
                self.update_options_to_draw()
            # move cursor to the beginning
            elif c == KEY_START or c == KEY_CTRL_A:
                self.search_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == KEY_END or c == KEY_CTRL_E:
                self.search_t.move_cursor_to_end()
            # normal search char
            elif type(c) is str:
                if self.search_t.add_string(c, self.data_manager.get_forbidden_chars()):
                    self.option_to_draw = None
                    self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.get_number_options_to_draw())
                    # update the options to show
                    self.update_options_to_draw(initialize_index=True)
            elif type(c) is int:
                logging.debug("loop select - integer input not handled: " + repr(c))
            else:
                logging.error("loop select - input not handled: " + repr(c))

