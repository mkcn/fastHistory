import logging

from parser.bashParser import BashParser
from parser.manParser import ManParser
from database.dataManager import DataManager
from pick.pageGeneric import PageGeneric


class PageInfo(PageGeneric):
    """
    Class to draw the info page
    """
    INDENT = 2
    SUB_TITLE_LEN = 15

    MIN_BLOCK_NUM_TO_SHOW_TAGS = 1
    MIN_BLOCK_NUM_TO_SHOW_DESCRIPTION = 2

    MESSAGE_NO_TAG = "To add a tag press "
    MESSAGE_NO_DESC = "To add a description press "
    MESSAGE_NO_MAN_PAGE_AVAILABLE = "No info available"

    def __init__(self, drawer, option, search_filters, context_shift, blocks_shift=0, data_from_man_page=None):
        """
        initialize page info drawer

        :param drawer:                  drawer obj
        :param option:                  selected option
        :param search_filters:          array of strings used to filter options
        :param context_shift:           context shift obj
        :param blocks_shift:            blocks shift number
        :param data_from_man_page:      data retrieved from the man page
        """
        PageGeneric.__init__(self, drawer)
        self.option = option
        self.search_filters = search_filters
        self.context_shift = context_shift
        self.data_from_man_page = data_from_man_page
        self.cursor_y = 0

        self.blocks_shift = blocks_shift

    def update_option_value(self, option):
        """
        update option value, this is called when the data is changed and must be reloaded (e.g. edit tag)

        :param option:
        :return:
        """
        self.option = option

    def shift_blocks_down(self):
        """
        move blocks down to show one block less
        :return:
        """
        if self.blocks_shift < 2:
            self.blocks_shift += 1

    def shift_blocks_up(self):
        """
        move blocks up to show one block more
        :return:
        """
        if self.blocks_shift > 0:
            self.blocks_shift -= 1

    def get_blocks_shift(self):
        return self.blocks_shift

    def draw_page(self):
        """
        draw option line (the one of which the user want to have more info)

        :return:
        """
        # draw colored title
        self.drawer.draw_row(self.CHAR_SPACE * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("Info selected command", x=2, color=self.drawer.color_columns_title)

        # draw option row
        self.draw_option(option=self.option,
                         search_filters=self.search_filters,
                         selected=True,
                         context_shift=self.context_shift,
                         last_column_size=0)
        self.drawer.new_line()

        if self.search_filters[DataManager.INPUT.INDEX_IS_ADVANCED]:
            self.draw_info_tags(tags=self.option[DataManager.OPTION.INDEX_TAGS],
                                filter_tags=self.search_filters[DataManager.INPUT.INDEX_TAGS])
            self.draw_info_description(desc=self.option[DataManager.OPTION.INDEX_DESC],
                                       filter_desc=self.search_filters[DataManager.INPUT.INDEX_DESC_WORDS])
        else:
            self.draw_info_tags(tags=self.option[DataManager.OPTION.INDEX_TAGS],
                                filter_tags=self.search_filters[DataManager.INPUT.INDEX_MAIN_WORDS])
            self.draw_info_description(desc=self.option[DataManager.OPTION.INDEX_DESC],
                                       filter_desc=self.search_filters[DataManager.INPUT.INDEX_MAIN_WORDS])

        self.draw_info_man_page(data_from_man_page=self.data_from_man_page)
        # help line in the last line
        self._draw_help_line_info()
        # cursor set position
        self.drawer.hide_cursor()

    def _draw_help_line_info(self):
        """
        Draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Select", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Go back", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Canc", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Delete", x_indent=1, allow_last_row=True)

        self.drawer.draw_row(self.CHAR_EDIT, x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Edit", x_indent=1, allow_last_row=True)

        self.drawer.draw_row(self.CHAR_TAG, x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Tag", x_indent=1, allow_last_row=True)

        self.drawer.draw_row(self.CHAR_DESCRIPTION, x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Description", x_indent=1, allow_last_row=True)

    def draw_info_tags(self, tags, filter_tags):
        """
        draw tags section

        :param tags:            array of tags
        :param filter_tags:     tag filters
        :return:
        """
        if self.blocks_shift < self.MIN_BLOCK_NUM_TO_SHOW_TAGS:
            self.drawer.new_line()
            self.drawer.draw_row(self.CHAR_SPACE * self.SUB_TITLE_LEN, x=self.INDENT, color=self.drawer.color_columns_title)
            self.drawer.draw_row("Tags", x=self.INDENT + 1, color=self.drawer.color_columns_title)
            self.drawer.new_line()
            self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
            if tags is not None and len(tags) > 0:
                for tag in tags:
                    self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag)
                    found = False
                    for filter_tag in filter_tags:
                        # TODO make more efficient (use the index tag value)
                        index_tag = tag.lower().find(filter_tag)
                        if index_tag != -1:
                            found = True
                            self.draw_marked_string(tag, filter_tag, color_marked=self.drawer.color_search)
                            break
                    if not found:
                        self.drawer.draw_row(tag)
                    self.drawer.draw_row(self.CHAR_SPACE)
            else:
                self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
                self.drawer.draw_row(self.MESSAGE_NO_TAG)
                self.drawer.draw_row(self.CHAR_TAG + "]", color=self.drawer.color_hash_tag)
            self.drawer.new_line()
            self.cursor_y += 3

    def draw_info_description(self, desc, filter_desc):
        """
        draw description section

        :param desc:            description string
        :param filter_desc:     description filter
        :return:
        """
        if self.blocks_shift < self.MIN_BLOCK_NUM_TO_SHOW_DESCRIPTION:
            self.drawer.new_line()
            self.drawer.draw_row(self.CHAR_SPACE * self.SUB_TITLE_LEN, x=self.INDENT, color=self.drawer.color_columns_title)
            self.drawer.draw_row("Description", x=self.INDENT + 1, color=self.drawer.color_columns_title)
            self.drawer.new_line()
            self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
            if desc is not None and len(desc) > 0:
                self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag)
                self.draw_marked_string(desc, filter_desc, color_marked=self.drawer.color_search)
            else:
                self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
                self.drawer.draw_row(self.MESSAGE_NO_DESC)
                self.drawer.draw_row(self.CHAR_DESCRIPTION + "]", color=self.drawer.color_hash_tag)
            self.drawer.new_line()

    def draw_info_man_page(self, data_from_man_page):
        """
        draw man info section

        :param data_from_man_page:  object with man info
        :return:
        """
        self.drawer.new_line()
        self.drawer.draw_row(self.CHAR_SPACE * self.SUB_TITLE_LEN, x=self.INDENT, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Man page info", x=self.INDENT + 1, color=self.drawer.color_columns_title)

        # these information are calculate when the cmd is selected
        # iterate for each cmd (one bash string can contain more commands) and print all the flags
        info_man_shown = False
        self.drawer.new_line()

        if data_from_man_page is not None:
            for item in data_from_man_page:
                cmd_main = item[BashParser.INDEX_CMD]
                cmd_flags = item[BashParser.INDEX_FLAGS]
                # cmd meaning found in the man page
                if cmd_main[BashParser.INDEX_MEANING]:
                    info_man_shown = True
                    self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
                    self.drawer.draw_row(cmd_main[BashParser.INDEX_VALUE], color=self.drawer.color_selected_row)
                    self.drawer.draw_row(": ")
                    # the cmd meaning could be on more line
                    self._draw_cmd_meaning(None, cmd_main[BashParser.INDEX_MEANING])
                    # print each flag meaning
                    for flag in cmd_flags:
                        # if flag found in the man page
                        if flag[BashParser.INDEX_MEANING]:
                            self._draw_cmd_meaning([flag[BashParser.INDEX_VALUE]], flag[BashParser.INDEX_MEANING],
                                                   is_flag=True)
                    self.drawer.new_line()
        if not info_man_shown:
            self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
            self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
            self.drawer.draw_row(self.MESSAGE_NO_MAN_PAGE_AVAILABLE)
            self.drawer.draw_row("]", color=self.drawer.color_hash_tag)

    def _draw_cmd_meaning(self, word_to_underline, meaning_obj, is_flag=False):
        """
        given the meaning of a cmd or of a relative flag, it prints the each line with different indentations.
        this will create a sort of tree effect to easily detect which flags belong to which command
        :param word_to_underline:
        :param meaning_obj:
        :param is_flag:
        :return:
        """
        if is_flag:
            indent = 4
        else:
            indent = 2
        indent_more = 6

        for row in meaning_obj:
            if row[ManParser.INDEX_IS_FIRST_LINE]:
                self.drawer.draw_row(self.CHAR_SPACE * indent)
                self.draw_marked_string(row[ManParser.INDEX_MEANING_VALUE],
                                        word_to_underline,
                                        color_marked=self.drawer.color_selected_row,
                                        case_sensitive=True,
                                        recursive=False)
            else:
                self.drawer.draw_row(self.CHAR_SPACE)
                self.drawer.draw_row(self.CHAR_SPACE * indent_more)
                self.drawer.draw_row(row[ManParser.INDEX_MEANING_VALUE])
            self.drawer.new_line()

    def draw_input_error_msg(self, input_error_msg, row):
        """
        draw label with error message to show about the input

        :param input_error_msg:             string error to show or None
        :param row:                         row number where to show the error message
        :return:
        """
        if input_error_msg is not None:
            self.drawer.set_y(row)
            self.drawer.draw_row(self.CHAR_SPACE + "Invalid input ", x_indent=2, color=self.drawer.color_search)
            self.drawer.draw_row(self.CHAR_SPACE + input_error_msg + self.CHAR_SPACE, color=self.drawer.color_selected_row)