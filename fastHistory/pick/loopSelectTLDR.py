import logging

from fastHistory import ConsoleUtils
from fastHistory.console import consoleUtils
from fastHistory.parser.InputData import InputData
from fastHistory.parser.inputParser import InputParser
from fastHistory.pick.textManager import ContextShifter
from fastHistory.pick.keys import Keys
from fastHistory.pick.pageSelectTLDR import PageSelectTLDR
from fastHistory.tldr.tldrParser import TLDRParser, ParsedTLDRExample
from fastHistory.tldr.tldrParserThread import TLDRParseThread


class LoopSelectTLDR(object):
    """
    Class to draw the page with the commands to select
    """

    SELECTED_COMMAND_ENDING = " #"

    def __init__(self, drawer, search_text):
        self.drawer = drawer
        self.search_field = search_text

        self.tldr_options: list = []
        self.tldr_options_draw: list = []
        self.tldr_options_index: int = 0
        self.tldr_options_draw_index: int = 0

        self.tldr_examples: ParsedTLDRExample = ParsedTLDRExample()
        self.tldr_examples_draw: list = []
        self.tldr_examples_index: int = 0
        self.tldr_examples_draw_index: int = 0
        self.example_content_shift = ContextShifter()

        self.focus = PageSelectTLDR.Focus.AREA_FILES

    def run_loop_tldr(self, cached_in_memory_pages):
        """
        :return:
        """
        tldr_parser = TLDRParser(cached_in_memory_pages)
        tldr_parser_thread = None
        input_data = InputData(False, "", [])
        tldr_options_reload_needed = True
        tldr_options_waiting = True
        tldr_examples_reload_needed = True
        tldr_ui_reload = True
        msg_to_show = None

        page_tldr_search = PageSelectTLDR(self.drawer)

        while True:
            # TODO fix "alt+d" crash
            if tldr_options_reload_needed:
                tldr_options_reload_needed = False
                input_data = InputParser.parse_input(self.search_field.get_text_lower(), is_search_mode=True)
                if tldr_parser_thread:
                    tldr_parser_thread.stop()
                tldr_parser_thread = TLDRParseThread(tldr_parser, input_data)
                tldr_parser_thread.start()
                tldr_options_waiting = True

            if tldr_options_waiting and not tldr_parser_thread.is_alive():
                tldr_options_waiting = False
                self.tldr_options = tldr_parser_thread.get_result_tldr_options()
                self.update_tldr_options_to_draw()
                tldr_examples_reload_needed = True
                tldr_ui_reload = True

            if tldr_examples_reload_needed:
                tldr_examples_reload_needed = False
                if len(self.tldr_options_draw) > 0:
                    tldr_page_match = self.tldr_options_draw[self.tldr_options_draw_index]
                    self.tldr_examples = tldr_parser.get_tldr_cmd_examples(tldr_page_match)
                    self.update_tldr_example_to_draw()
                    self.update_tldr_options_to_draw_cmd_availability()
                    # reset example index
                    self.tldr_examples_index = self.tldr_examples.get_first_example_index()
                    self.tldr_examples_draw_index = self.tldr_examples_index
                else:
                    self.tldr_examples = ParsedTLDRExample()
                    self.tldr_examples_index = 0
                    self.tldr_examples_draw = []

            if page_tldr_search.has_minimum_size():
                page_tldr_search.draw_page(
                    search_filters=self.search_field,
                    input_data=input_data,
                    tldr_options_draw=self.tldr_options_draw,
                    tldr_options_draw_index=self.tldr_options_draw_index,
                    tldr_examples_draw=self.tldr_examples_draw,
                    example_draw_index=self.tldr_examples_draw_index,
                    example_content_shift=self.example_content_shift,
                    focus_area=self.focus,
                    has_url_more_info=self.tldr_examples.has_url_more_info(),
                    is_waiting=tldr_options_waiting,
                    msg_to_show=msg_to_show)

            if msg_to_show:
                msg_to_show = None

            # wait for char
            c = self.drawer.wait_next_char(multi_threading_mode=tldr_parser_thread.is_alive())
            logging.debug("pressed key: %s" % repr(c))

            tldr_ui_reload = True
            if c == Keys.KEY_TIMEOUT:
                tldr_ui_reload = False
                continue
            elif c in Keys.KEYS_ENTER:
                selected_example = self.get_selected_example(search_input=input_data)
                if selected_example:
                    return [True, [True, selected_example]]
            elif c == Keys.KEY_CTRL_SPACE:
                example_to_copy = self.get_selected_example(search_input=input_data, copied=True)
                if example_to_copy:
                    msg_to_show = ConsoleUtils.copy_to_clipboard(example_to_copy, show_data_in_msg=False)[1]
            elif c == Keys.KEY_CTRL_L:
                if self.tldr_examples.has_url_more_info():
                    msg_to_show = ConsoleUtils.copy_to_clipboard(self.tldr_examples.get_url_more_info())[1]
            elif c == Keys.KEY_CTRL_E:
                res = ConsoleUtils.copy_to_clipboard(self.tldr_examples.get_tldr_github_page())
                msg_to_show = res[1]
            elif c == Keys.KEY_TAB:
                self.flip_focus()
            # go back to main page
            elif c == Keys.KEY_CTRL_F or c == Keys.KEY_CTRL_D or c == Keys.KEY_ESC:
                return [False, 0]
            elif c == Keys.KEY_UP:
                if self.move_up():
                    tldr_examples_reload_needed = True
            elif c == Keys.KEY_DOWN:
                if self.move_down():
                    tldr_examples_reload_needed = True
            # -> command
            elif c == Keys.KEY_RIGHT:
                self.move_right()
            # <- command
            elif c == Keys.KEY_LEFT:
                self.move_left()
            # this occurs when the console size changes
            elif c == Keys.KEY_RESIZE:
                self.drawer.reset()
                self.search_field.set_max_x(self.drawer.get_max_x(), with_margin_x=True)
                self.update_tldr_options_to_draw()
            # move cursor to the beginning
            elif c == Keys.KEY_START or c == Keys.KEY_CTRL_A:
                self.search_field.move_cursor_to_start()
                self.example_content_shift.reset_context_shifted()
                self.focus = PageSelectTLDR.Focus.AREA_FILES
            # move cursor to the end
            elif c == Keys.KEY_CTRL_E:
                self.search_field.move_cursor_to_end()
                self.example_content_shift.reset_context_shifted()
                self.focus = PageSelectTLDR.Focus.AREA_FILES
            elif c == Keys.KEY_CTRL_U:
                if self.search_field.set_text(""):
                    tldr_options_reload_needed = True
            # delete a char of the search
            elif c in Keys.KEYS_DELETE:
                if self.delete_char():
                    tldr_options_reload_needed = True
            # normal search char
            elif type(c) is str:
                if self.add_str(c):
                    tldr_options_reload_needed = True
            else:
                logging.error("input not handled: %s" % repr(c))

    def get_selected_example(self, search_input: InputData, copied: bool = False):
        """
        if copied is false, it adds all the search words as tags (es. selected_command #word1 #word2)
        :param search_input:
        :param copied:
        :return:
        """
        res = self.tldr_examples.get_current_selected_example(self.tldr_examples_index)
        if res is None:
            return None
        if not copied:
            ending = ""
            for item in search_input.get_all_words():
                if len(item) > 0:
                    ending += self.SELECTED_COMMAND_ENDING + item.strip()
            if ending == "":
                ending += self.SELECTED_COMMAND_ENDING
            res += ending

        if self.focus == PageSelectTLDR.Focus.AREA_EXAMPLES:
            return res
        else:
            self.focus = PageSelectTLDR.Focus.AREA_EXAMPLES
            self.search_field.move_cursor_to_end()
            return None

    def move_up(self):
        """
        :return: true if the selected example needs to be changed
        """
        number_tldr_lines_to_draw = self.get_number_tldr_lines_to_draw()
        if self.focus == PageSelectTLDR.Focus.AREA_FILES:
            if self.tldr_options_index > 0:
                self.tldr_options_index -= 1
                # the current line is the first line
                if self.tldr_options_draw_index == 0:
                    self.tldr_options_draw = self.tldr_options[self.tldr_options_index:self.tldr_options_index + number_tldr_lines_to_draw]
                else:
                    self.tldr_options_draw_index -= 1
                return True
            return False
        elif self.focus == PageSelectTLDR.Focus.AREA_EXAMPLES:
            delta_previous_example_index = self.tldr_examples.get_delta_previous_example_index(self.tldr_examples_index)
            if delta_previous_example_index > 0:
                self.tldr_examples_index -= delta_previous_example_index
                # the current line is the first line
                if self.tldr_examples_draw_index - delta_previous_example_index < 0:
                    self.tldr_examples_draw = self.tldr_examples.get_rows()[
                                             self.tldr_examples_index:self.tldr_examples_index + number_tldr_lines_to_draw]
                    self.tldr_examples_draw_index = 0
                else:
                    self.tldr_examples_draw_index -= delta_previous_example_index
            else:
                # reset view to default
                self.tldr_examples_draw = self.tldr_examples.get_rows()[:number_tldr_lines_to_draw]
                self.tldr_examples_draw_index = self.tldr_examples.get_first_example_index()
            return False
        else:
            logging.error("out of focus")
            return False

    def move_down(self):
        """
        :return: true if the selected example needs to be changed
        """
        number_tldr_lines_to_draw = self.get_number_tldr_lines_to_draw()
        if self.focus == PageSelectTLDR.Focus.AREA_FILES:
            if self.tldr_options_index + 1 < len(self.tldr_options):
                self.tldr_options_index += 1
                # # the current line is the last line
                # # current line starts from 0
                if self.tldr_options_draw_index + 1 >= number_tldr_lines_to_draw:
                    # array   [0,1,2,3,4,5]
                    #            |   |
                    # pointer        *
                    # start   3(pointer)-3(n option to draw) + 1 = 1
                    # end     3(pointer) + 1  = 4
                    # result  [0,1,2,3,4,5][1:4] = [1,2,3]
                    self.tldr_options_draw = self.tldr_options[
                                             self.tldr_options_index + 1 - number_tldr_lines_to_draw:self.tldr_options_index + 1]
                else:
                    self.tldr_options_draw_index += 1
                return True
            else:
                return False
        elif self.focus == PageSelectTLDR.Focus.AREA_EXAMPLES:
            next_example_delta_index = self.tldr_examples.get_delta_next_example_index(self.tldr_examples_index)
            if next_example_delta_index > 0:
                self.tldr_examples_index += next_example_delta_index
                if self.tldr_examples_draw_index + next_example_delta_index >= number_tldr_lines_to_draw:
                    # data          [x,E,x,x,E,x,x,E,x]
                    # array         [0,1,2,3,4,5,6,7,8]
                    # old window     |   |
                    # old index        *
                    # new window         |   |
                    # new index              *    <-- 1 + 3 (delta) = 4
                    # start   4(index)-3(windows) + 1 = 2
                    # end     4(pointer) + 1  = 5
                    # result  [0,1,2,3,4,5,6,7,8][2:5] = [2,3,4]
                    self.tldr_examples_draw = self.tldr_examples.get_rows()[
                                             self.tldr_examples_index + 1 - number_tldr_lines_to_draw:self.tldr_examples_index + 1]
                    self.tldr_examples_draw_index = number_tldr_lines_to_draw - 1
                else:
                    self.tldr_examples_draw_index += next_example_delta_index
            return False
        else:
            logging.error("out of focus")
            return False

    def move_right(self):
        if self.focus == PageSelectTLDR.Focus.AREA_FILES:
            if self.search_field.is_cursor_at_the_end():
                self.focus = PageSelectTLDR.Focus.AREA_EXAMPLES
            else:
                self.search_field.move_cursor_right()
        elif self.focus == PageSelectTLDR.Focus.AREA_EXAMPLES:
            self.example_content_shift.shift_context_right()
        else:
            logging.error("out of focus")

    def move_left(self):
        if self.focus == PageSelectTLDR.Focus.AREA_EXAMPLES:
            if not self.example_content_shift.is_context_index_zero():
                self.example_content_shift.shift_context_left()
            else:
                self.focus = PageSelectTLDR.Focus.AREA_FILES
        elif self.focus == PageSelectTLDR.Focus.AREA_FILES:
            if not self.search_field.is_cursor_at_the_beginning():
                self.search_field.move_cursor_left()
        else:
            logging.error("out of focus")

    def reset_indexes(self):
        self.tldr_options_index = 0
        self.tldr_options_draw_index = 0

        self.tldr_examples_index = 0
        self.tldr_examples_draw_index = 0

    def update_tldr_options_to_draw(self):
        number_lines_to_draw = self.get_number_tldr_lines_to_draw()
        # check if the current selected line is too big set the last line as selected line
        # this is needed for the console resize event
        if self.tldr_options_draw_index >= number_lines_to_draw:
            self.tldr_options_index -= self.tldr_options_draw_index - number_lines_to_draw + 1
            self.tldr_options_draw_index = number_lines_to_draw - 1

        # option            a,b,c,d,e,f
        # option_i          0,1,2,3,4,5
        # index             \-----*
        # windows               0,1,2
        # current_line          \-*
        # wanted result         c,d,e
        # start point       = 3 - 1 = 2
        # end point         = 2 + 3 + 1 = 5
        # result            -> [a,b,c,d,e,f][3:5] = [c,d,e]
        self.tldr_options_draw = self.tldr_options[
                              self.tldr_options_index - self.tldr_options_draw_index:
                              self.tldr_options_index - self.tldr_options_draw_index + number_lines_to_draw]

    def update_tldr_options_to_draw_cmd_availability(self):
        """
        the check is done only once for command (included with move_up and move_down) unless the input change
        :return:
        """
        for tldr_item in self.tldr_options_draw:
            if tldr_item[TLDRParser.INDEX_TLDR_MATCH_AVAILABILITY] is None:
                tldr_item[TLDRParser.INDEX_TLDR_MATCH_AVAILABILITY] = ConsoleUtils.is_cmd_available_on_this_machine(
                    tldr_item[TLDRParser.INDEX_TLDR_MATCH_CMD])

    def update_tldr_example_to_draw(self):
        number_lines_to_draw = self.get_number_tldr_lines_to_draw()
        # check if the current selected line is too big set the last line as selected line
        # this is needed for the console resize event
        if self.tldr_examples_draw_index >= number_lines_to_draw:
            self.tldr_examples_index -= self.tldr_examples_draw_index - number_lines_to_draw + 1
            self.tldr_examples_draw_index = number_lines_to_draw - 1

        self.tldr_examples_draw = self.tldr_examples.get_rows()[
                                  self.tldr_examples_index - self.tldr_examples_draw_index:
                                  self.tldr_examples_index - self.tldr_examples_draw_index + number_lines_to_draw]

    def get_number_tldr_lines_to_draw(self):
        """
        get total number of options which can be drawn
        this is calculated as the max y - 3: 1 for the title, 1 for the column title and 1 for the last info line
        :return:
        """
        return self.drawer.get_max_y() - 3

    def add_str(self, c):
        # TODO use self.data_manager.get_forbidden_chars())
        if self.search_field.add_string(c, ['\n', '\r']):
            self.reset_indexes()
            return True
        else:
            return False

    def delete_char(self):
        if self.search_field.delete_char():
            self.reset_indexes()
            return True
        else:
            return False

    def flip_focus(self):
        if self.focus != PageSelectTLDR.Focus.AREA_EXAMPLES:
            self.focus = PageSelectTLDR.Focus.AREA_EXAMPLES
            self.search_field.move_cursor_to_end()
        else:
            self.focus = PageSelectTLDR.Focus.AREA_FILES
            self.example_content_shift.reset_context_shifted()

    def get_updated_search_str(self):
        return self.search_field.get_text()
