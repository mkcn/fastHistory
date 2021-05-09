import logging
import time

from fastHistory.pick.pageGeneric import PageGeneric
from fastHistory.pick.textManager import ContextShifter
from fastHistory.tldr.tldrParser import ParsedTLDRExample, TLDRParser

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastHistory.parser.InputData import InputData
    from fastHistory.pick.textManager import TextManager


class PageTLDRSearchDrawer(PageGeneric):
    """
    Class to draw the page with the commands to select
    """

    FILE_COLUMN_NAME = "Command"
    EXAMPLE_COLUMN_NAME = "Examples from tldr-pages"
    MSG_WAITING = "Loading.."
    MSG_NO_MATCH = "No match found"
    MSG_NO_EXAMPLE = "No example found"

    SEARCH_FIELD_MARGIN = 23
    TLDR_PAGES_COLUMN_SIZE = 27

    class Focus:
        AREA_FILES = 0
        AREA_EXAMPLES = 1

    def __init__(self, drawer):
        PageGeneric.__init__(self, drawer)
        self.last_words_to_mark = []

    def draw_page(self,
                  search_filters: "TextManager",
                  input_data: "InputData",
                  example_content_shift: "ContextShifter",
                  tldr_options_draw: list,
                  tldr_examples_draw: list,
                  example_draw_index: int = 0,
                  tldr_options_draw_index: int = 0,
                  focus_area: Focus = Focus.AREA_FILES,
                  has_url_more_info: bool = False,
                  is_waiting: bool = False):
        """
        :return:
        """
        self.clean_page()

        logging.debug("draw page PageTLDRSearch")
        self.drawer.draw_row(self.TITLE_DEFAULT)
        title_len = len(self.TITLE_DEFAULT)
        self.drawer.draw_row(": ")
        title_len += 2
        search_text = search_filters.get_text_to_print()

        # search text
        if input_data.is_advanced():
            if input_data.get_main_str() != "":
                # find index of cmd filter in search text (e.g. "what" in "what #cmd @desc")
                index_cmd = search_text.find(input_data.get_main_str())
                if index_cmd != -1:
                    # print until the end of the cmd option
                    index_cmd_end = index_cmd + len(input_data.get_main_str())
                    self.drawer.draw_row(search_text[0:index_cmd])
                    self.drawer.draw_row(search_text[index_cmd:index_cmd_end])
                    # cut string with unprinted section
                    search_text = search_text[index_cmd_end:]
                else:
                    logging.error("option cmd string not found in search field: %s" % input_data.get_main_str())

            for tag in input_data.get_tags(strict=True):
                # find index of tag filter in search text (e.g. "cmd" in "what #cmd @desc")
                index_tag = search_text.find(tag)
                if index_tag != -1:
                    # print until the end of the cmd option
                    index_tag_end = index_tag + len(tag)
                    self.drawer.draw_row(search_text[0:index_tag], color=self.drawer.color_hash_tag_disable)
                    self.drawer.draw_row(search_text[index_tag:index_tag_end])
                    # cut string with unprinted section
                    search_text = search_text[index_tag_end:]
                else:
                    logging.error("option tag string not found in search field: %s" % tag)

            if input_data.get_description_str() is not None:
                # find index of desc filter in search text (e.g. "desc" in "what #cmd @desc")
                index_desc = search_text.find(input_data.get_description_str())
                if index_desc != -1:
                    # print until the end of the cmd option
                    index_desc_end = index_desc + len(input_data.get_description_str())
                    self.drawer.draw_row(search_text[0:index_desc], color=self.drawer.color_hash_tag_disable)
                    self.drawer.draw_row(search_text[index_desc:index_desc_end])
                    # cut string with unprinted section
                    search_text = search_text[index_desc_end:]
                else:
                    logging.error("option tag string not found in search field: %s" % input_data.get_description_str())
            # print the rest of the unprinted text
            # NOTE: this is printed with color and it can contain "#" and "@"
            self.drawer.draw_row(search_text, color=self.drawer.color_hash_tag_disable)
        else:
            self.drawer.draw_row(search_text, color=self.drawer.color_search_input)

        # draw tabs
        size_tab_1 = len(self.TAB_NAME_MY_LIST)
        size_tab_2 = len(self.TAB_NAME_TLDR)
        max_x = self.drawer.get_max_x()
        self.drawer.draw_row(self.TAB_NAME_MY_LIST, x=max_x - size_tab_1 - size_tab_2 - 1, color=self.drawer.color_tab_no_focus)
        self.drawer.draw_row(self.TAB_NAME_TLDR, x=max_x-size_tab_2 - 1, color=self.drawer.color_tab_focus)

        # columns titles
        self.drawer.new_line()
        self.drawer.fill_row(color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.FILE_COLUMN_NAME, x=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.EXAMPLE_COLUMN_NAME, x=self.TLDR_PAGES_COLUMN_SIZE + 2,
                             color=self.drawer.color_columns_title)

        self.drawer.new_line()

        current_y = self.drawer.get_y()
        if is_waiting:
            words_to_mark = self.last_words_to_mark
        else:
            words_to_mark = input_data.get_all_words()
            self.last_words_to_mark = words_to_mark

        # draw tldr command options
        if self.draw_command_column(tldr_options_draw,
                                    words_to_mark,
                                    tldr_options_draw_index,
                                    focus_area == self.Focus.AREA_FILES,
                                    is_waiting):
            # draw tldr examples
            self.drawer.set_y(y=current_y, x=self.TLDR_PAGES_COLUMN_SIZE+2)
            self.draw_example_column(tldr_examples_draw,
                                     words_to_mark,
                                     example_draw_index,
                                     example_content_shift,
                                     focus_area == self.Focus.AREA_EXAMPLES)

        # help line in the last line
        self._draw_help_line_selector(is_focus_examples=focus_area == self.Focus.AREA_EXAMPLES,
                                      has_url_more_info=has_url_more_info)

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(title_len + search_filters.get_cursor_index_to_print(), 0)

        self.refresh_page()

    def draw_command_column(self, tldr_options_draw, words_to_mark, selected_command_index, has_focus, is_waiting):
        number_options = len(tldr_options_draw)
        if number_options == 0:
            if is_waiting:
                self.draw_just_msg(msg=self.MSG_WAITING)
            else:
                self.draw_just_msg(msg=self.MSG_NO_MATCH)
            return False
        else:
            command_context_shifter = ContextShifter()
            for i in range(number_options):
                tldr_item = tldr_options_draw[i]
                value_tldr_folder = tldr_item[TLDRParser.INDEX_TLDR_MATCH_CMD_FOLDER] + "/"
                if tldr_item[TLDRParser.INDEX_TLDR_MATCH_AVAILABILITY]:
                    value_tldr_folder = "+" + value_tldr_folder
                else:
                    value_tldr_folder = " " + value_tldr_folder
                if i == selected_command_index:
                    if has_focus:
                        background_color = self.drawer.color_selected_row
                    else:
                        background_color = self.drawer.color_selected_row_no_focus
                else:
                    background_color = self.drawer.NULL_COLOR

                self.drawer.draw_row(value_tldr_folder, color=background_color)
                # add parameter
                value_tldr_cmd = command_context_shifter.get_text_shifted(tldr_item[TLDRParser.INDEX_TLDR_MATCH_CMD], self.TLDR_PAGES_COLUMN_SIZE - 1 - len(value_tldr_folder))
                self.draw_marked_string(value_tldr_cmd,
                                        words_to_mark,
                                        recursive=True,
                                        color_marked=self.drawer.color_search,
                                        color_default=background_color)
                if i == selected_command_index:
                    self.drawer.fill_row(color=background_color, max_x=self.TLDR_PAGES_COLUMN_SIZE - 1)
                self.drawer.new_line()
            return True

    def draw_example_column(self, tldr_examples_draw, words_to_mark, example_draw_index, example_content_shift, has_focus):
        if len(tldr_examples_draw) == 0:
            self.draw_just_msg(msg=self.MSG_NO_EXAMPLE)
        else:
            tldr_example_column_size = self.drawer.get_max_x() - self.TLDR_PAGES_COLUMN_SIZE
            self.drawer.set_x(self.TLDR_PAGES_COLUMN_SIZE)
            for i in range(len(tldr_examples_draw)):
                row_type = tldr_examples_draw[i][ParsedTLDRExample.INDEX_EXAMPLE_TYPE]
                row_value = tldr_examples_draw[i][ParsedTLDRExample.INDEX_EXAMPLE_VALUE]
                complete_background_row = False
                if row_type == ParsedTLDRExample.Type.EXAMPLE:
                    if i == example_draw_index:
                        if has_focus:
                            background_color = self.drawer.color_selected_row
                            complete_background_row = True
                        else:
                            background_color = self.drawer.color_cmd_sample
                    else:
                        background_color = self.drawer.color_cmd_sample
                else:
                    background_color = self.drawer.NULL_COLOR
                row_value = example_content_shift.get_text_shifted(row_value, tldr_example_column_size)
                # set starting point because we are in the second column
                self.drawer.set_x(self.TLDR_PAGES_COLUMN_SIZE)
                self.draw_marked_string(row_value,
                                        words_to_mark,
                                        recursive=True,
                                        color_marked=self.drawer.color_search,
                                        color_default=background_color)
                if complete_background_row:
                    self.drawer.fill_row(color=background_color, max_x=self.drawer.get_max_x() - 1)
                self.drawer.new_line()

    def draw_just_msg(self, msg: str, x: int = 0):
        shift = 1
        for y in range(int(self.drawer.get_max_y()/2 - shift)):
            self.drawer.new_line()
        msg_space = int((self.drawer.get_max_x() - x) / 2 - len(msg) / 2 - 1)
        self.drawer.fill_row(x=x, max_x=msg_space)
        self.drawer.draw_row(msg)

    def _draw_help_line_selector(self, is_focus_examples: bool, has_url_more_info: bool):
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        if is_focus_examples:
            self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
            self.drawer.draw_row("Select", x_indent=1, allow_last_row=True)
        else:
            self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
            self.drawer.draw_row("Get examples", x_indent=1, allow_last_row=True)

        if is_focus_examples:
            self.drawer.draw_row("Ctrl+space", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
            self.drawer.draw_row("Copy", x_indent=1, allow_last_row=True)

        if has_url_more_info:
            self.drawer.draw_row("Ctrl+l", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
            self.drawer.draw_row("Copy link", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+f", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("My list", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+c", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Exit", x_indent=1, allow_last_row=True)

