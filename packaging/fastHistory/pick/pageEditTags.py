from fastHistory.database.dataManager import DataManager
from fastHistory.pick.pageInfo import PageInfo


class PageEditTags(PageInfo):
    """
    Class to draw the tags page
    whit this page the user can edit the tags list of the current selected command
    """

    def __init__(self, drawer, option, search_filters, context_shift):
        """
        initialize page edit tags

        :param drawer:              drawer obj
        :param option:              selected option
        :param search_filters:     search input obj with input string and filters
        :param context_shift:       context shift obj
        """
        PageInfo.__init__(self, drawer, option, search_filters, context_shift)

    def draw_page_edit(self, tags_text, tags_cursor_index, input_error_msg=None, data_from_man_page=None):
        """
        draw page to edit tags of the current selected option

        :param tags_text:              tags string
        :param tags_cursor_index:      position of the cursor
        :param input_error_msg:        string error to show, None if there is no error to show
        :param data_from_man_page:      data retrieved from the man page
        :return:
        """
        # draw colored title
        self.drawer.draw_row(self.CHAR_SPACE * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("# Tags edit", x=2, color=self.drawer.color_columns_title)

        # draw option row
        self.draw_option(option=self.option,
                         search_filters=self.search_filters,
                         selected=True,
                         context_shift=self.context_shift,
                         last_column_size=0)

        self.drawer.new_line()
        self._draw_edit_tag_field(tags_text)

        self.draw_info_description(desc=self.option[DataManager.OPTION.INDEX_DESC],
                                   filter_desc=self.search_filters.get_description_words())

        self.draw_info_man_page(data_from_man_page)

        self.cursor_y = 4
        self.draw_input_error_msg(input_error_msg, self.cursor_y - 1)

        # help line in the last line
        self._draw_help_line_info()

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(self.INDENT + tags_cursor_index, self.cursor_y)

    def _draw_edit_tag_field(self, new_tags_str):
        """
        draw input tags field

        :param new_tags_str:   current tags string
        :return:
        """
        self.drawer.new_line()
        # note: to highlight we use the same color of the selected row
        self.drawer.draw_row(self.CHAR_SPACE * self.SUB_TITLE_LEN, x=self.INDENT, color=self.drawer.color_selected_row)
        self.drawer.draw_row("Tags", x=self.INDENT + 1, color=self.drawer.color_selected_row)
        self.drawer.new_line()
        self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
        self.draw_marked_string(new_tags_str, [self.CHAR_TAG], color_marked=self.drawer.color_hash_tag)
        self.drawer.new_line()

    def _draw_help_line_info(self):
        """
        draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Save", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Go back without saving", x_indent=1, allow_last_row=True)