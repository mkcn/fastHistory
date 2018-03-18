from parser.bashParser import BashParser
from parser.manParser import ManParser
from database.dataRetriever import DataRetriever


class PageInfo(object):
    """
    Class to draw the info page
    """

    def __init__(self, drawer, debug_line, page_selector):
        self.drawer = drawer
        self.debug_line = debug_line
        self.page_selector = page_selector

    def draw_page_info(self, option, search_text_lower, flags_for_info_cmd):
        """
        draw info option
        :return:
        """
        # draw colored title
        self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("Info selected command", x=2, color=self.drawer.color_columns_title)

        # options
        value_option = option

        # draw option row
        self.page_selector.draw_option(cmd=value_option[DataRetriever.INDEX_OPTION_CMD],
                                       tags=value_option[DataRetriever.INDEX_OPTION_TAGS],
                                       desc=value_option[DataRetriever.INDEX_OPTION_DESC],
                                       search=search_text_lower,
                                       selected=True,
                                       last_column_size=0)
        self.drawer.new_line()
        self.draw_info_option(cmd_string=value_option[DataRetriever.INDEX_OPTION_CMD],
                              tags=value_option[DataRetriever.INDEX_OPTION_TAGS],
                              desc=value_option[DataRetriever.INDEX_OPTION_DESC],
                              search_text=search_text_lower,
                              flags_for_info_cmd=flags_for_info_cmd)

        # help line in the last line
        self.draw_help_line_info()

        # cursor set position
        self.drawer.move_cursor(9, 4)

    def draw_help_line_info(self):
        """
        Draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Shift-tab", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Go back", x_indent=1)

        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Select", x_indent=1)

        self.drawer.draw_row("<-|->", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Scroll", x_indent=1)

    def draw_info_option(self, cmd_string, tags, desc, search_text, flags_for_info_cmd):
        indent = 2
        sub_title_len = 15

        char_column = " "

        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Tags", x=indent + 1, color=self.drawer.color_columns_title)
        self.drawer.new_line()
        self.drawer.draw_row(" " * indent)
        for tag in tags:
            self.drawer.draw_row("#", color=self.drawer.color_hash_tag)
            self.draw_marked_string(tag, search_text)
            self.drawer.draw_row(" ")
        self.drawer.new_line()

        # description if not empty

        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Description", x=indent + 1, color=self.drawer.color_columns_title)
        self.drawer.new_line()
        self.drawer.draw_row("@", x=indent, color=self.drawer.color_hash_tag)
        self.draw_marked_string(desc, search_text)
        self.drawer.new_line()

        self.drawer.new_line()
        self.drawer.draw_row(" " * sub_title_len, x=indent, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Man page info", x=indent + 1, color=self.drawer.color_columns_title)

        # these information are calculate when the cmd is selected
        # iterate for each cmd (one bash string can contain more commands) and print all the flags
        info_man_shown = False
        for item in flags_for_info_cmd:
            cmd_main = item[BashParser.INDEX_CMD]
            cmd_flags = item[BashParser.INDEX_FLAGS]
            # cmd meaning found in the man page
            if cmd_main[BashParser.INDEX_MEANING]:
                info_man_shown = True
                self.drawer.new_line()
                self.drawer.draw_row(char_column)
                self.drawer.draw_row(" ")
                self.drawer.draw_row(cmd_main[BashParser.INDEX_VALUE], color=self.drawer.color_selected_row)
                self.drawer.draw_row(": ")
                # the cmd meaning could be on more line
                for line in cmd_main[BashParser.INDEX_MEANING]:
                    self.drawer.draw_row(line[ManParser.INDEX_MEANING_VALUE])

                # print each flag meaning
                for flag in cmd_flags:
                    # if flag found in the man page
                    if flag[BashParser.INDEX_MEANING]:
                        self.draw_cmd_flag_meaning(flag[BashParser.INDEX_VALUE], flag[BashParser.INDEX_MEANING])
                self.drawer.new_line()
        if not info_man_shown:
            self.drawer.new_line()
            self.drawer.draw_row(char_column)
            self.drawer.draw_row(" ")
            self.drawer.draw_row("No info available")

    def draw_cmd_flag_meaning(self, flag, flag_meaning):

        indent_flag = 4
        indent_flag_more = 6

        for row in flag_meaning:
            self.drawer.new_line()
            if row[ManParser.INDEX_IS_FIRST_LINE]:
                self.drawer.draw_row(" " * indent_flag)
                self.draw_marked_string(row[ManParser.INDEX_MEANING_VALUE],
                                        flag,
                                        color_marked=self.drawer.color_selected_row,
                                        case_sensitive=True,
                                        recursive=False)
            else:
                self.drawer.draw_row(" ")
                self.drawer.draw_row(" " * (indent_flag + indent_flag_more))
                self.drawer.draw_row(row[ManParser.INDEX_MEANING_VALUE])

    def draw_marked_string(self, text, sub_str, index_sub_str=None, color_default=1, color_marked=None,
                           case_sensitive=False, recursive=True):
        """
        Given a string and a sub string it will print the string with the sub string of a different color

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
        if len(sub_str) == 0:
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
