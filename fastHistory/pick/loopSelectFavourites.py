import logging

from fastHistory import DataManager
from fastHistory.pick.keys import Keys
from fastHistory.pick.loopInfo import LoopInfo
from fastHistory.pick.pageSelectFavourites import PageSelectFavourites
from fastHistory.pick.textManager import ContextShifter


class LoopSelectFavourites(object):

    def __init__(self, drawer, data_manager, search_t, last_column_size, multi_select=False):

        self.drawer = drawer
        self.data_manager = data_manager
        self.search_t = search_t
        self.multi_select = multi_select
        self.last_column_size = last_column_size

        self.all_selected = []
        self.context_shift = ContextShifter()
        self.index = 0  # TODO rename with options_index
        self.current_line_index = 0  # TODO rename with options_to_draw_index
        self.options = None
        self.option_to_draw = None

        self.page_selector = PageSelectFavourites(self.drawer)

    def run_loop_select(self):
        """
        Loop to capture user input keys to interact with the select page

        """
        # get filtered starting options
        self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.get_number_options_to_draw())
        self.initialize_options_to_draw()

        while True:
            if self.page_selector.has_minimum_size():
                self.page_selector.draw_page(
                    search_filters=self.data_manager.get_search_filters(),
                    options=self.get_options(),
                    search_t=self.search_t,
                    context_shift=self.context_shift,
                    last_column_size=self.last_column_size)

            # wait for char
            c = self.drawer.wait_next_char()
            logging.debug("pressed key: %s" % repr(c))

            if c == Keys.KEY_TIMEOUT:
                continue
            elif c == Keys.KEY_UP:
                self.move_up()
            elif c == Keys.KEY_DOWN:
                self.move_down()
                # retrieve more data from db when user want to view more
                if self.index % (self.get_number_options_to_draw() - 1) == 0:
                    self.options = self.data_manager.filter(
                        self.search_t.get_text_lower(),
                        self.index + self.get_number_options_to_draw())
            elif c in Keys.KEYS_ENTER:
                return [True, [True, self.get_selected_and_update_db()]]
            elif c == Keys.KEY_CTRL_SPACE:
                return [True, [False, self.get_selected_and_update_db()]]
            # note: currently not implemented
            elif c == Keys.KEY_SELECT and self.multi_select:
                self.mark_index()
            # tab command
            elif c == Keys.KEY_TAB:
                # reset index of search text (to avoid confusion when the scroll is done on the info page)
                self.search_t.move_cursor_to_end()
                while 1:
                    loop_info = LoopInfo(self.get_current_selected_option(),
                                         self.drawer,
                                         self.data_manager,
                                         self.search_t,
                                         self.last_column_size,
                                         self.context_shift,
                                         self.multi_select)
                    res = loop_info.run_loop_info()
                    if res[0]:
                        if res[1] == "select":
                            return [True, [True, self.get_selected_and_update_db()]]
                        else:  # res[1] == "copy":
                            return [True, [False, self.get_selected_and_update_db()]]
                    else:
                        if res[1] == "update":
                            self.loop_select_options_reload()
                            continue
                        elif res[1] == "command_update":
                            self.loop_select_options_reload()
                            self.adjust_index_after_command_edit(new_command=res[2])
                            continue
                        elif res[1] == "deleted":
                            self.loop_select_options_reload()
                            break
                        else:  # res[1] == None
                            break
            # search TLDR
            elif c == Keys.KEY_CTRL_T:
                return [False, 2]
            elif c == Keys.KEY_CTRL_R:  
                # TO IMPLEMENT this will open a bash history tab
                pass
                return [False, 1]
            # -> command
            elif c == Keys.KEY_RIGHT:
                if self.search_t.is_cursor_at_the_end():
                    if self.options != []:
                        # move all options list to right
                        self.context_shift.shift_context_right()
                else:
                    self.search_t.move_cursor_right()
            # <- command
            elif c == Keys.KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not self.search_t.is_cursor_at_the_beginning():
                    self.search_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in Keys.KEYS_DELETE:
                if self.search_t.delete_char():
                    self.loop_select_options_reload(True)
            # delete current selected option
            elif c == Keys.KEY_CANC:
                current_selected_option = self.get_current_selected_option()
                if self.data_manager.delete_element(current_selected_option[DataManager.OPTION.INDEX_CMD]):
                    self.loop_select_options_reload(False)
            elif c == Keys.KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                self.search_t.set_max_x(self.drawer.get_max_x(), with_margin_x=True)
                # TODO make this more efficient
                self.loop_select_options_reload(False)
            elif c == Keys.KEY_START or c == Keys.KEY_CTRL_A:
                self.search_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            elif c == Keys.KEY_END or c == Keys.KEY_CTRL_E:
                self.search_t.move_cursor_to_end()
            elif c == Keys.KEY_CTRL_U:
                self.search_t.set_text("")
                self.loop_select_options_reload(True)
            elif type(c) is str:
                if self.search_t.add_string(c, self.data_manager.get_forbidden_chars()):
                    self.loop_select_options_reload(True)
            else:
                logging.error("input not handled: %s" % repr(c))

    def adjust_index_after_command_edit(self, new_command):
        """
        if an other item exists with the new command text, it is
        deleted and merged with the old command item by the db function.
        In this case the GUI index must be correctly adjusted
        :return:
        """
        current_selected_option = self.get_current_selected_option()
        if current_selected_option[DataManager.OPTION.INDEX_CMD] != new_command:
            self.move_up()

    def get_number_options_to_draw(self):
        """
        get total number of options which can be drawn
        this is calculated as the max y - 3: 1 for the title, 1 for the column title and 1 for the last info line
        :return:
        """
        return self.drawer.get_max_y() - 3

    def initialize_options_to_draw(self):
        """
        initialize the variable "option to draw" based on the size of the screen

        :return:
        """
        number_option_to_draw = self.get_number_options_to_draw()
        self.option_to_draw = self.options[0:number_option_to_draw]

    def move_up(self):
        """
        if it is not already on the first line move up
        :return:
        """
        if self.index > 0:
            self.index -= 1
            # the current line is the first line
            if self.current_line_index == 0:
                number_option_to_draw = self.drawer.get_max_y() - 3
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

    def loop_select_options_reload(self, initialize_index=False):
        # reset shift value
        if initialize_index:
            self.context_shift.reset_context_shifted()
            self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.get_number_options_to_draw())
        else:
            self.options = self.data_manager.filter(self.search_t.get_text_lower(), self.index + self.get_number_options_to_draw())
        self.update_options_to_draw(initialize_index=initialize_index)

    def mark_index(self):
        """
        method not used yet to support multi selection
        :return:
        """
        if self.multi_select:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)

    def get_options(self):
        tmp_options = []
        for row_index, option in enumerate(self.option_to_draw):
            if row_index == self.current_line_index:
                tmp_options.append([True, option])
            else:
                tmp_options.append([False, option])
        return tmp_options

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

    def get_selected_and_update_db(self):
        """
        :return: the current selected option
        """
        option_count = len(self.options)
        if option_count == 0 or self.index >= option_count or self.index < 0:
            return ""
        selected_cmd = self.options[self.index][DataManager.OPTION.INDEX_CMD]
        # move selected command on top
        self.data_manager.update_selected_element_order(selected_cmd)
        return selected_cmd

    def get_current_selected_option(self):
        for row_index, option in enumerate(self.option_to_draw):
            if row_index == self.current_line_index:
                return option
