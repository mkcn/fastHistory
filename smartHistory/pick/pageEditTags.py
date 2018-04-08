from database.dataManager import DataManager


class PageEditTags(object):
    """
    Class to draw the tags page
    whit this page the user can edit the tags list
    """

    def __init__(self, drawer, page_selector):
        self.drawer = drawer
        self.page_selector = page_selector

    def draw_page(self, option, search_text_lower):
        """
        draw tag page
        :return:
        """
        # draw colored title
        self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row("# Tags edit", x=2, color=self.drawer.color_columns_title)

        # options
        value_option = option

        # draw option row
        self.page_selector.draw_option(cmd=value_option[DataManager.INDEX_OPTION_CMD],
                                       tags=value_option[DataManager.INDEX_OPTION_TAGS],
                                       desc=value_option[DataManager.INDEX_OPTION_DESC],
                                       search=search_text_lower,
                                       selected=True,
                                       last_column_size=0)
        self.drawer.new_line()
        self.drawer.new_line()

        index = 2

        self.drawer.draw_row(" " * index)
        self.drawer.draw_row("[", color=self.drawer.color_hash_tag)
        self.drawer.draw_row("this feature is not implemented yet")
        self.drawer.draw_row("]", color=self.drawer.color_hash_tag)

        # help line in the last line
        self.draw_help_line_info()

        # cursor set position
        self.drawer.hide_cursor()

    def draw_help_line_info(self):
        """
        Draw info at the end of the console
        :return:
        """
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Save", x_indent=1)

        self.drawer.draw_row("<-|->", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Scroll", x_indent=1)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Go back without saving", x_indent=1)
