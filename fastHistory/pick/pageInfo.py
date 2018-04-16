import logging

from parser.bashParser import BashParser
from parser.manParser import ManParser
from database.dataManager import DataManager


class PageInfo(object):
    """
    Class to draw the info page
    """

    def __init__(self, drawer, page_selector):
        self.drawer = drawer
        self.page_selector = page_selector

    def draw_page_info(self, option, filters, data_from_man_page):
        """
        draw option line (the one of which the user want to have more info)

        :param option:                  selected option
        :param filters:                 strings used to filter description (in default search there are the same)
        :param data_from_man_page:      data retrieved from the man page
        :return:
        """
        # draw colored title
        self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("Info selected command", x=2, color=self.drawer.color_columns_title)

        # options
        value_option = option

        # draw option row
        self.page_selector.draw_option(cmd=value_option[DataManager.INDEX_OPTION_CMD],
                                       tags=value_option[DataManager.INDEX_OPTION_TAGS],
                                       desc=value_option[DataManager.INDEX_OPTION_DESC],
                                       filter_cmd=filters[DataManager.INDEX_OPTION_CMD],
                                       filter_desc=filters[DataManager.INDEX_OPTION_DESC],
                                       filter_tags=filters[DataManager.INDEX_OPTION_TAGS],
                                       selected=True,
                                       last_column_size=0)
        self.drawer.new_line()
        self._draw_info_option(tags=value_option[DataManager.INDEX_OPTION_TAGS],
                               desc=value_option[DataManager.INDEX_OPTION_DESC],
                               filter_desc=filters[DataManager.INDEX_OPTION_DESC],
                               filter_tags=filters[DataManager.INDEX_OPTION_TAGS],
                               data_from_man_page=data_from_man_page)

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
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Select", x_indent=1)

        self.drawer.draw_row("<-|->", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Scroll", x_indent=1)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Go back", x_indent=1)

        self.drawer.draw_row("Canc", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Delete", x_indent=1)

        self.drawer.draw_row("#", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Tag", x_indent=1)

        self.drawer.draw_row("@", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Description", x_indent=1)

    def _draw_info_option(self, tags, desc, filter_desc, filter_tags, data_from_man_page):
        indent = 2
        sub_title_len = 15

        char_column = " "

        no_tag_message = "To add a tag press "
        no_desc_message = "To add a description press "
        no_man_page_available = "No info available"

        # tags in not empty
        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Tags", x=indent + 1, color=self.drawer.color_columns_title)
        self.drawer.new_line()
        self.drawer.draw_row(" " * indent)
        if tags is not None and len(tags) > 0:
            for tag in tags:
                self.drawer.draw_row("#", color=self.drawer.color_hash_tag)
                found = False
                for filter_tag in filter_tags:
                    index_tag = tag.lower().find(filter_tag)
                    if index_tag != -1:
                        found = True
                        self.draw_marked_string(tag, filter_tag)
                        break
                if not found:
                    self.drawer.draw_row(tag)
                self.drawer.draw_row(" ")
        else:
            self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
            self.drawer.draw_row(no_tag_message)
            self.drawer.draw_row("#]", color=self.drawer.color_hash_tag)
        self.drawer.new_line()

        # description if not empty
        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Description", x=indent + 1, color=self.drawer.color_columns_title)
        self.drawer.new_line()
        self.drawer.draw_row(" " * indent)
        if desc is not None and len(desc) > 0:
            self.drawer.draw_row("@", color=self.drawer.color_hash_tag)
            self.draw_marked_string(desc, filter_desc)
        else:
            self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
            self.drawer.draw_row(no_desc_message)
            self.drawer.draw_row("@]", color=self.drawer.color_hash_tag)
        self.drawer.new_line()

        # man page info
        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Man page info", x=indent + 1, color=self.drawer.color_columns_title)

        # these information are calculate when the cmd is selected
        # iterate for each cmd (one bash string can contain more commands) and print all the flags
        info_man_shown = False
        self.drawer.new_line()

        for item in data_from_man_page:
            cmd_main = item[BashParser.INDEX_CMD]
            cmd_flags = item[BashParser.INDEX_FLAGS]
            # cmd meaning found in the man page
            if cmd_main[BashParser.INDEX_MEANING]:
                info_man_shown = True
                self.drawer.draw_row(char_column)
                self.drawer.draw_row(" ")
                self.drawer.draw_row(cmd_main[BashParser.INDEX_VALUE], color=self.drawer.color_selected_row)
                self.drawer.draw_row(": ")
                # the cmd meaning could be on more line
                self.draw_cmd_meaning(None, cmd_main[BashParser.INDEX_MEANING])
                # print each flag meaning
                for flag in cmd_flags:
                    # if flag found in the man page
                    if flag[BashParser.INDEX_MEANING]:
                        self.draw_cmd_meaning(flag[BashParser.INDEX_VALUE], flag[BashParser.INDEX_MEANING], is_flag=True)
                self.drawer.new_line()
        if not info_man_shown:
            self.drawer.draw_row(" " * indent)
            self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
            self.drawer.draw_row(no_man_page_available)
            self.drawer.draw_row("]", color=self.drawer.color_hash_tag)

    def draw_cmd_meaning(self, word_to_underline, meaning_obj, is_flag=False):
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
                self.drawer.draw_row(" " * indent)
                self.draw_marked_string(row[ManParser.INDEX_MEANING_VALUE],
                                        word_to_underline,
                                        color_marked=self.drawer.color_selected_row,
                                        case_sensitive=True,
                                        recursive=False)
            else:
                self.drawer.draw_row(" ")
                self.drawer.draw_row(" " * indent_more)
                self.drawer.draw_row(row[ManParser.INDEX_MEANING_VALUE])
            self.drawer.new_line()

    def draw_marked_string(self, text, sub_str, index_sub_str=None, color_default=1, color_marked=None,
                           case_sensitive=False, recursive=True):
        """
        Given a string and a sub string it will print the string with the sub string of a different color
        TODO use the function from page Select or create a common class

        :param text:             string to print
        :param sub_str:          sub string to print with a different color
        :param index_sub_str:    if already available
        :param color_default:    default color
        :param color_marked:     color sub string
        :param case_sensitive:   case sensitive search
        :param recursive:        if False stop the search at the first match, if True search all matches recursively
        :return:
        """
        # if sub string is empty draw normally the text
        if sub_str is None or len(sub_str) == 0:
            self.drawer.draw_row(text, color=color_default)
        else:
            if len(text) > 0:
                if index_sub_str is None:
                    if not case_sensitive:
                        search_text = text.lower()
                        search_sub_str = sub_str.lower()
                    else:
                        search_text = text
                        search_sub_str = sub_str
                    index_sub_str = search_text.find(search_sub_str)
                if color_marked is None:
                    color_marked = self.drawer.color_search
                len_sub_str = len(sub_str)

                if index_sub_str is not -1:
                    # print first section of str
                    self.drawer.draw_row(text[:index_sub_str], color=color_default)
                    # print marked section of str
                    self.drawer.draw_row(text[index_sub_str:index_sub_str + len_sub_str], color=color_marked)
                    # print final section of str
                    if recursive:
                        self.draw_marked_string(text[index_sub_str + len_sub_str:],
                                                sub_str,
                                                color_default=color_default,
                                                color_marked=color_marked)
                    else:
                        self.drawer.draw_row(text[index_sub_str + len_sub_str:], color=color_default)
                else:
                    self.drawer.draw_row(text, color=color_default)
