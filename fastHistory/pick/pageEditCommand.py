from database.dataManager import DataManager
from pick.pageInfo import PageInfo


class PageEditCommand(PageInfo):
    """
    Class to draw the command edit page
    whit this page the user can edit the current selected command
    """

    def __init__(self, drawer, option, search_filters, context_shift, blocks_shift, data_from_man_page):
        """
        initialize page command description

        :param drawer:          drawer obj
        :param option:          selected option
        :param search_filters:  array of strings used to filter options
        :param context_shift:   context shift obj
        :param blocks_shift:    blocks shift number
        :param data_from_man_page:  obj with man info
        """
        PageInfo.__init__(self, drawer, option, search_filters, context_shift, blocks_shift, data_from_man_page)

    def draw_page_edit(self, command_text, command_cursor_index, input_error_msg=None):
        """
        draw page to edit the command of the current selected option

        :param command_text:            command string
        :param command_cursor_index:    position of the cursor
        :param input_error_msg:         string error to show. None if there is no error to show
        :return:
        """
        # draw colored title
        self.drawer.draw_row(self.CHAR_SPACE * (self.drawer.get_max_x()), color=self.drawer.color_selected_row)
        self.drawer.draw_row("Command edit", x=2, color=self.drawer.color_selected_row)

        # draw option row
        self._draw_edit_command_field(command_text)

        self.draw_info_tags(tags=self.option[DataManager.OPTION.INDEX_TAGS],
                            filter_tags=self.search_filters.get_tags())
        self.draw_info_description(desc=self.option[DataManager.OPTION.INDEX_DESC],
                                   filter_desc=self.search_filters.get_description_words())

        self.draw_info_man_page(data_from_man_page=self.data_from_man_page)

        self.cursor_y = 1
        self.draw_input_error_msg(input_error_msg, self.cursor_y - 1)

        # help line in the last line
        self._draw_help_line_info()

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(self.INDENT + command_cursor_index, self.cursor_y)

    def _draw_edit_command_field(self, new_command_str):
        """
        draw input command field

        :param new_command_str:   current command string
        :return:
        """
        self.drawer.new_line()
        self.drawer.draw_row(self.CHAR_SPACE * self.INDENT)
        self.drawer.draw_row(new_command_str)
        self.drawer.new_line()

    def _draw_help_line_info(self):
        """
        draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter ", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Save", allow_last_row=True)

        self.drawer.draw_row("Tab ", x_indent=2, color=self.drawer.color_columns_title, allow_last_row=True)
        self.drawer.draw_row("Go back without saving", allow_last_row=True)


