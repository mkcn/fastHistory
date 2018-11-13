from database.dataManager import DataManager
from pick.pageInfo import PageInfo


class PageEditDescription(PageInfo):
    """
    Class to draw the description page
    whit this page the user can edit the description of the current selected command
    """

    def __init__(self, drawer, option, filters, context_shift, data_from_man_page):
        """
        initialize page edit description

        :param drawer:          drawer obj
        :param option:          selected option
        :param filters:         strings used to highlight filtered strings (in default search there are the same)
        :param context_shift:   context shift obj
        :param data_from_man_page:  obj with man info
        """
        PageInfo.__init__(self, drawer, option, filters, context_shift, data_from_man_page)

    def draw_page_edit(self, description_text, description_cursor_index, input_error_msg):
        """
        draw page to edit the description of the current selected option

        :param description_text:            description string
        :param description_cursor_index:    position of the cursor
        :param input_error_msg:             string error to show, None is there is no error to show
        :return:
        """
        # draw colored title
        self.drawer.draw_row(self.CHAR_SPACE * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("@ Description edit", x=2, color=self.drawer.color_columns_title)

        # draw option row
        self.draw_option(cmd=self.option[DataManager.INDEX_OPTION_CMD],
                         tags=self.option[DataManager.INDEX_OPTION_TAGS],
                         desc=self.option[DataManager.INDEX_OPTION_DESC],
                         filter_cmd=self.filters[DataManager.INDEX_OPTION_CMD],
                         filter_desc=self.filters[DataManager.INDEX_OPTION_DESC],
                         filter_tags=self.filters[DataManager.INDEX_OPTION_TAGS],
                         selected=True,
                         context_shift=self.context_shift,
                         last_column_size=0)
        self.drawer.new_line()

        self.draw_info_tags(tags=self.option[DataManager.INDEX_OPTION_TAGS],
                            filter_tags=self.filters[DataManager.INDEX_OPTION_TAGS])
        self._draw_edit_description_field(description_text)
        self.draw_info_man_page(data_from_man_page=self.data_from_man_page)

        self.draw_input_error_msg(input_error_msg, 6)

        # help line in the last line
        self._draw_help_line_info()

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(self.INDENT + description_cursor_index, 7)

    def _draw_edit_description_field(self, new_description_str):
        """
        draw input tags field

        :param new_description_str:   current description string
        :return:
        """
        self.drawer.new_line()
        # note: to highlight we use the same color of the selected row
        self.drawer.draw_row(self.CHAR_SPACE * self.SUB_TITLE_LEN, x=self.INDENT, color=self.drawer.color_selected_row)
        self.drawer.draw_row("Description", x=self.INDENT + 1, color=self.drawer.color_selected_row)
        self.drawer.new_line()
        self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
        self.draw_marked_string(new_description_str, self.CHAR_DESCRIPTION, color_marked=self.drawer.color_hash_tag)
        self.drawer.new_line()

    def _draw_help_line_info(self):
        """
        draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Save", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("<-|->", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Scroll", x_indent=1, allow_last_row=True)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Go back without saving", x_indent=1, allow_last_row=True)


