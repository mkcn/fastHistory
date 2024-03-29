import logging

from fastHistory.pick.pageGeneric import PageGeneric


class PageSelectFavourites(PageGeneric):
    """
    Class to draw the page with the commands to select
    """

    CMD_COLUMN_NAME = "Commands"
    TAG_AND_DESCRIPTION_COLUMN_NAME = "Tags & Description"

    INDEX_SELECTED_TRUE = 0
    INDEX_SELECTED_VALUE = 1

    DEBUG_MODE = False

    def __init__(self, drawer):
        PageGeneric.__init__(self, drawer)

    def draw_page(self, search_filters, options, search_t, context_shift, last_column_size, msg_to_show=None):
        """
        draw page where the user can select the command

        :param options:         list of options to draw
        :param search_t:        search obj insert by the user to search options
        :param context_shift:   context shift obj
        :param search_filters:         filters (derived from the search_text) used to filter the options
        :param last_column_size:size of last column (tag and description column)
        :return:
        """
        self.clean_page()
        # title
        self.drawer.draw_row(self.TITLE_DEFAULT)
        title_len = len(self.TITLE_DEFAULT)
        self.drawer.draw_row(": ")
        title_len += 2

        search_text = search_t.get_text_to_print()

        # search text
        if search_filters.is_advanced():
            if search_filters.get_main_str() != "":
                # find index of cmd filter in search text (e.g. "what" in "what #cmd @desc")
                index_cmd = search_text.find(search_filters.get_main_str())
                if index_cmd != -1:
                    # print until the end of the cmd option
                    index_cmd_end = index_cmd + len(search_filters.get_main_str())
                    self.drawer.draw_row(search_text[0:index_cmd])
                    self.drawer.draw_row(search_text[index_cmd:index_cmd_end])
                    # cut string with unprinted section
                    search_text = search_text[index_cmd_end:]
                else:
                    logging.error("option cmd string not found in search field: %s" % search_filters.get_main_str())

            for tag in search_filters.get_tags(strict=True):
                # find index of tag filter in search text (e.g. "cmd" in "what #cmd @desc")
                index_tag = search_text.find(tag)
                if index_tag != -1:
                    # print until the end of the cmd option
                    index_tag_end = index_tag + len(tag)
                    self.drawer.draw_row(search_text[0:index_tag], color=self.drawer.color_hash_tag)
                    self.drawer.draw_row(search_text[index_tag:index_tag_end])
                    # cut string with unprinted section
                    search_text = search_text[index_tag_end:]
                else:
                    logging.error("option tag string not found in search field: %s" % tag)

            if search_filters.get_description_str() is not None:
                # find index of desc filter in search text (e.g. "desc" in "what #cmd @desc")
                index_desc = search_text.find(search_filters.get_description_str())
                if index_desc != -1:
                    # print until the end of the cmd option
                    index_desc_end = index_desc + len(search_filters.get_description_str())
                    self.drawer.draw_row(search_text[0:index_desc], color=self.drawer.color_hash_tag)
                    self.drawer.draw_row(search_text[index_desc:index_desc_end])
                    # cut string with unprinted section
                    search_text = search_text[index_desc_end:]
                else:
                    logging.error("option tag string not found in search field: %s" % search_filters.get_description_str())

            # print the rest of the unprinted text
            # NOTE: this is printed with color and it can contain "#" and "@"
            self.drawer.draw_row(search_text, color=self.drawer.color_hash_tag)
        else:
            self.drawer.draw_row(search_text, color=self.drawer.color_search_input)

        # draw tabs
        size_tab_1 = len(self.TAB_NAME_MY_LIST)
        size_tab_2 = len(self.TAB_NAME_TLDR)
        max_x = self.drawer.get_max_x()
        self.drawer.draw_row(self.TAB_NAME_MY_LIST, x=max_x - size_tab_1 - size_tab_2 - 1, color=self.drawer.color_tab_focus)
        self.drawer.draw_row(self.TAB_NAME_TLDR, x=max_x - size_tab_2 - 1, color=self.drawer.color_tab_no_focus)

        # columns titles
        index_tab_column = int(self.drawer.get_max_x() * last_column_size / 100)

        # draw row colored
        self.drawer.new_line()
        self.drawer.fill_row(color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.CMD_COLUMN_NAME, x=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.TAG_AND_DESCRIPTION_COLUMN_NAME, x=self.drawer.max_x - index_tab_column,
                             color=self.drawer.color_columns_title)

        # options
        number_options = len(options)
        if number_options == 0:
            self.draw_no_result(search_filters=search_filters)
        else:
            for i in range(number_options):
                selected = options[i][self.INDEX_SELECTED_TRUE]
                value_option = options[i][self.INDEX_SELECTED_VALUE]

                # draw option row
                self.draw_option(option=value_option,
                                 search_filters=search_filters,
                                 selected=selected,
                                 context_shift=context_shift,
                                 last_column_size=index_tab_column)
        # last line
        if msg_to_show:
            self.draw_msg_to_show(msg_to_show)
        else:
            self._draw_help_line_selector()

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(title_len + search_t.get_cursor_index_to_print(), 0)

        self.refresh_page()

    def draw_no_result(self, search_filters):
        """
        draw "no result" info

        :param search_filters: filters used by the user
        :return:
        """
        msg_no_result = "no result"
        msg_try_tldr_1 = "use "
        msg_try_tldr_2 = "ctrl+d"
        msg_try_tldr_3 = " to Discover more commands"
        if search_filters.is_advanced():
            shift = 3
        else:
            shift = 1

        for y in range(int(self.drawer.get_max_y()/2 - shift)):
            self.drawer.new_line()
        msg_no_result_space = int(self.drawer.get_max_x()/2 - len(msg_no_result)/2 - 1)
        msg_try_tldr_space = int(self.drawer.get_max_x()/2 - len(msg_try_tldr_1 + msg_try_tldr_2 + msg_try_tldr_3)/2 - 1)

        self.drawer.draw_row(msg_no_result, x=msg_no_result_space)
        self.drawer.new_line()
        self.drawer.draw_row(msg_try_tldr_1, x=msg_try_tldr_space)
        self.drawer.draw_row(msg_try_tldr_2, color=self.drawer.color_columns_title)
        self.drawer.draw_row(msg_try_tldr_3)
        self.drawer.new_line()
        self.drawer.new_line()

        if search_filters.is_advanced():
            msg_help_title = " Advanced search syntax "
            msg_help = "[command_filter] [#tag_filter ...] [@description_filter]"

            msg_space = int(self.drawer.get_max_x() / 2 - len(msg_help_title) / 2)
            self.drawer.fill_row(max_x=msg_space)
            self.drawer.draw_row(msg_help_title, color=self.drawer.color_columns_title)

            self.drawer.new_line()
            msg_space = int(self.drawer.get_max_x() / 2 - len(msg_help) / 2)
            self.drawer.fill_row(max_x=msg_space)
            self.drawer.draw_row(msg_help)

    def _draw_help_line_selector(self):
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Select", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+space", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Copy", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Tab", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("More", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+d", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Discover", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Del", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Delete", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Ctrl+c", x_indent=1, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Exit", x_indent=1, allow_last_row=True)