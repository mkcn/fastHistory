import logging


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

    TITLE_DEFAULT = "TLDR search"

    FILE_COLUMN_NAME = "Command"
    EXAMPLE_COLUMN_NAME = "Examples from tldr-pages"

    DEBUG_MODE = False

    SEARCH_FIELD_MARGIN = 23
    TLDR_PAGES_COLUMN_SIZE = 27

    class Focus:
        AREA_FILES = 0
        AREA_EXAMPLES = 1

    def __init__(self, drawer):
        PageGeneric.__init__(self, drawer)

    def draw_page(self,
                  search_filters: "TextManager",
                  input_data: "InputData",
                  tldr_options_draw: list,
                  tldr_options_draw_index: int,
                  tldr_examples_draw: list,
                  example_draw_index: int,
                  example_content_shift: "ContextShifter",
                  focus_area: Focus):
        """
        # TODO check and re-write

        :return:
        """
        logging.debug("PageTLDRSearch - draw_page")
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
                    logging.error("option cmd string not found in search field: " + input_data.get_main_str())

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
                    logging.error("option tag string not found in search field: " + tag)

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
                    logging.error("option tag string not found in search field: " + input_data.get_description_str())
            # print the rest of the unprinted text
            # NOTE: this is printed with color and it can contain "#" and "@"
            self.drawer.draw_row(search_text, color=self.drawer.color_hash_tag_disable)
        else:
            self.drawer.draw_row(search_text, color=self.drawer.color_search_input)

        # columns titles
        self.drawer.new_line()
        self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.FILE_COLUMN_NAME, x=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.EXAMPLE_COLUMN_NAME, x=self.TLDR_PAGES_COLUMN_SIZE + 2,
                             color=self.drawer.color_columns_title)

        self.drawer.new_line()
        current_y = self.drawer.get_y()

        words_to_mark = input_data.get_all_words()

        # draw tldr command options
        self.draw_command_column(tldr_options_draw,
                                 words_to_mark,
                                 tldr_options_draw_index,
                                 focus_area == self.Focus.AREA_FILES)

        # draw tldr examples
        self.drawer.set_y(y=current_y, x=self.TLDR_PAGES_COLUMN_SIZE+2)
        self.draw_example_column(tldr_examples_draw,
                                 words_to_mark,
                                 example_draw_index,
                                 example_content_shift,
                                 focus_area == self.Focus.AREA_EXAMPLES)

        # help line in the last line
        self._draw_help_line_selector(focus_area == self.Focus.AREA_EXAMPLES)

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(title_len + search_filters.get_cursor_index_to_print(), 0)

    def draw_command_column(self, tldr_options_draw, words_to_mark, selected_command_index, has_focus):
        number_options = len(tldr_options_draw)
        if number_options == 0:
            self.draw_no_result(msg_no_result="no match found")
        else:
            command_context_shifter = ContextShifter()
            for i in range(number_options):
                tldr_item = tldr_options_draw[i]
                value_tldr_cmd = tldr_item[TLDRParser.INDEX_TLDR_MATCH_CMD_FOLDER] + "\\" + tldr_item[TLDRParser.INDEX_TLDR_MATCH_CMD]
                if tldr_item[TLDRParser.INDEX_TLDR_MATCH_AVAILABILITY]:
                    value_tldr_cmd = "+" + value_tldr_cmd
                else:
                    value_tldr_cmd = " " + value_tldr_cmd
                if i == selected_command_index:
                    if has_focus:
                        background_color = self.drawer.color_search
                    else:
                        background_color = self.drawer.color_selected_row  # TODO use a better name
                else:
                    background_color = self.drawer.NULL_COLOR
                value_tldr_cmd = command_context_shifter.get_text_shifted(value_tldr_cmd, self.TLDR_PAGES_COLUMN_SIZE - 1)
                self.draw_marked_string(value_tldr_cmd,
                                        words_to_mark,
                                        recursive=True,
                                        color_marked=self.drawer.color_search,
                                        color_default=background_color)
                self.drawer.new_line()

    def draw_example_column(self, tldr_examples_draw, words_to_mark, example_draw_index, example_content_shift, has_focus):
        if len(tldr_examples_draw) == 0:
            self.draw_no_result(msg_no_result="no example available")
        else:
            tldr_example_column_size = self.drawer.get_max_x() - self.TLDR_PAGES_COLUMN_SIZE
            self.drawer.set_x(self.TLDR_PAGES_COLUMN_SIZE)
            for i in range(len(tldr_examples_draw)):
                row_type = tldr_examples_draw[i][ParsedTLDRExample.INDEX_EXAMPLE_TYPE]
                row_value = tldr_examples_draw[i][ParsedTLDRExample.INDEX_EXAMPLE_VALUE]
                if row_type == ParsedTLDRExample.Type.EXAMPLE:
                    if i == example_draw_index:
                        if has_focus:
                            background_color = self.drawer.color_search  # TODO use a better name
                        else:
                            background_color = self.drawer.color_search_input
                    else:
                        background_color = self.drawer.color_search_input
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
                self.drawer.new_line()

    def draw_no_result(self, msg_no_result, x=0):
        shift = 1
        for y in range(int(self.drawer.get_max_y()/2 - shift)):
            self.drawer.new_line()
        msg_space = int((self.drawer.get_max_x() - x)/2 - len(msg_no_result)/2 - 1)

        self.drawer.draw_row(" " * msg_space, x=x)
        self.drawer.draw_row(msg_no_result)

    def _draw_help_line_selector(self, is_focus_examples: bool):
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

        self.drawer.draw_row("Ctrl+f", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Go back", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+c", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Exit", x_indent=1, allow_last_row=True)

