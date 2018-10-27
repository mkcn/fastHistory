import logging

from database.dataManager import DataManager


class PageSelector(object):
    """
    Class to draw the page with the commands to select
    """

    TITLE_DEFAULT = "Fast History search"
    TITLE_ADVANCE_SEARCH = " Advanced search   "

    CMD_COLUMN_NAME = "Commands"
    TAG_AND_DESCRIPTION_COLUMN_NAME = "Tags & Description"

    SELECTOR_START = ">"
    SELECTOR_END = "<"
    SELECTOR_NOT = " "

    INDEX_SELECTED_TRUE = 0
    INDEX_SELECTED_VALUE = 1

    DEBUG_MODE = False

    def __init__(self, drawer):
        self.drawer = drawer

    def draw_page_select(self, search_text, search_text_index, filters, options, last_column_size):
        """
        draw page where the user can select the command

        :param search_text:     string insert by the user to search options
        :param search_text_index: index of the cursor in the search text field
        :param filters:         filters (derived from the search_text) used to filter the options
        :param options:         list of options to draw
        :return:
        """
        # title
        if filters[DataManager.INDEX_OPTION_IS_ADVANCED]:
            self.drawer.draw_row(self.TITLE_ADVANCE_SEARCH, color=self.drawer.color_columns_title)
            title_len = len(self.TITLE_ADVANCE_SEARCH)
        else:
            self.drawer.draw_row(self.TITLE_DEFAULT)
            title_len = len(self.TITLE_DEFAULT)
        self.drawer.draw_row(": ")
        title_len += 2

        # search text
        if filters[DataManager.INDEX_OPTION_IS_ADVANCED]:

            if filters[DataManager.INDEX_OPTION_CMD] != "":
                # find index of cmd filter in search text (e.g. "what" in "what #cmd @desc")
                index_cmd = search_text.find(filters[DataManager.INDEX_OPTION_CMD])
                if index_cmd != -1:
                    # print until the end of the cmd option
                    index_cmd_end = index_cmd + len(filters[DataManager.INDEX_OPTION_CMD])
                    self.drawer.draw_row(search_text[0:index_cmd])
                    self.drawer.draw_row(search_text[index_cmd:index_cmd_end], color=self.drawer.color_search)
                    # cut string with unprinted section
                    search_text = search_text[index_cmd_end:]
                else:
                    logging.error("option cmd string not found in search field: " + filters[DataManager.INDEX_OPTION_CMD])

            for tag in filters[DataManager.INDEX_OPTION_TAGS]:
                # find index of tag filter in search text (e.g. "cmd" in "what #cmd @desc")
                index_tag = search_text.find(tag)
                if index_tag != -1:
                    # print until the end of the cmd option
                    index_tag_end = index_tag + len(tag)
                    self.drawer.draw_row(search_text[0:index_tag])
                    self.drawer.draw_row(search_text[index_tag:index_tag_end], color=self.drawer.color_search)
                    # cut string with unprinted section
                    search_text = search_text[index_tag_end:]
                else:
                    logging.error("option tag string not found in search field: " + tag)

            if filters[DataManager.INDEX_OPTION_DESC] is not None:
                # find index of desc filter in search text (e.g. "desc" in "what #cmd @desc")
                index_desc = search_text.find(filters[DataManager.INDEX_OPTION_DESC])
                if index_desc != -1:
                    # print until the end of the cmd option
                    index_desc_end = index_desc + len(filters[DataManager.INDEX_OPTION_DESC])
                    self.drawer.draw_row(search_text[0:index_desc])
                    self.drawer.draw_row(search_text[index_desc:index_desc_end], color=self.drawer.color_search)
                    # cut string with unprinted section
                    search_text = search_text[index_desc_end:]
                else:
                    logging.error("option tag string not found in search field: " + filters[DataManager.INDEX_OPTION_DESC])

            # print the rest of the unprinted text
            self.drawer.draw_row(search_text)
        else:
            self.drawer.draw_row(search_text, color=self.drawer.color_search)

        # columns titles
        index_tab_column = int(self.drawer.get_max_x() * last_column_size / 100)

        # draw row colored
        self.drawer.new_line()
        self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.CMD_COLUMN_NAME, x=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row(self.TAG_AND_DESCRIPTION_COLUMN_NAME, x=self.drawer.max_x - index_tab_column,
                             color=self.drawer.color_columns_title)

        # options
        number_options = len(options)
        if number_options == 0:
            self.draw_no_result(filters[DataManager.INDEX_OPTION_IS_ADVANCED])
        else:
            for i in range(number_options):
                selected = options[i][self.INDEX_SELECTED_TRUE]
                value_option = options[i][self.INDEX_SELECTED_VALUE]

                # draw option row
                self.draw_option(cmd=value_option[DataManager.INDEX_OPTION_CMD],
                                 desc=value_option[DataManager.INDEX_OPTION_DESC],
                                 tags=value_option[DataManager.INDEX_OPTION_TAGS],
                                 filter_cmd=filters[DataManager.INDEX_OPTION_CMD],
                                 filter_desc=filters[DataManager.INDEX_OPTION_DESC],
                                 filter_tags=filters[DataManager.INDEX_OPTION_TAGS],
                                 selected=selected,
                                 last_column_size=index_tab_column)

        # help line in the last line
        self._draw_help_line_selector()

        # cursor set position
        self.drawer.show_cursor()
        self.drawer.move_cursor(title_len + search_text_index, 0)

    def draw_no_result(self, is_advanced_search):
        """
        draw "no result" info

        :param is_advanced_search: if true draw also a short "advanced search syntax" help
        :return:
        """
        msg_no_result = "no result"
        if is_advanced_search:
            shift = 3
        else:
            shift = 1

        for y in range(int(self.drawer.get_max_y()/2 - shift)):
            self.drawer.new_line()
        msg_space = int(self.drawer.get_max_x()/2 - len(msg_no_result)/2 - 1)

        self.drawer.draw_row(" " * msg_space)
        self.drawer.draw_row(msg_no_result)

        self.drawer.new_line()
        self.drawer.new_line()
        if is_advanced_search:
            msg_help_title = " Advanced search syntax "
            msg_help = "[command_filter] [#tag_filter ...] [@description_filter]"

            msg_space = int(self.drawer.get_max_x() / 2 - len(msg_help_title) / 2)
            self.drawer.draw_row(" " * msg_space)
            self.drawer.draw_row(msg_help_title, color=self.drawer.color_columns_title)

            self.drawer.new_line()
            msg_space = int(self.drawer.get_max_x() / 2 - len(msg_help) / 2)
            self.drawer.draw_row(" " * msg_space)
            self.drawer.draw_row(msg_help)


    def draw_option(self, cmd, tags, desc, filter_cmd, filter_desc, filter_tags, last_column_size=0, selected=False):
        """
        draw option line

        :param cmd:                 bash command
        :param tags:                tags
        :param desc:                description
        :param filter_cmd:          string used to filter cmd
        :param filter_desc:         string used to filter description (in default search it is the same of filter_cmd)
        :param filter_tags:         string used to filter tags (in default search it is the same of filter_cmd)
        :param last_column_size:    tag and description column size
        :param selected:            if True the option is selected and underlined
        :return:
        """
        self.drawer.new_line()

        # if this option is selected set a background color
        if selected:
            background_color = self.drawer.color_selected_row
            # draw a colored line for the selected option
            self.drawer.draw_row(" " * (self.drawer.get_max_x()), color=background_color)
        else:
            background_color = self.drawer.NULL_COLOR

        # selector
        self.drawer.set_x(0)
        if selected:
            self.drawer.draw_row(self.SELECTOR_START, color=self.drawer.color_selector)
        else:
            self.drawer.draw_row(self.SELECTOR_NOT, color=background_color)
        self.drawer.draw_row(" ", color=background_color)

        #  cmd section
        cmd = self.drawer.shift_string(cmd, max_x=self.drawer.max_x - last_column_size - 3)
        self.draw_marked_string(cmd, filter_cmd, color_marked=self.drawer.color_search, color_default=background_color)

        if last_column_size:
            # tag and description section
            self.drawer.set_x(self.drawer.max_x - last_column_size - 1)

            tag_or_description_match = False

            # print matched tags

            unmatched_tags = []
            for tag in tags:
                found = False
                for filter_tag in filter_tags:
                    if filter_tag != "":
                        index_tag = tag.lower().find(filter_tag)
                        if index_tag != -1:
                            self.drawer.draw_row(" ", color=background_color)
                            self.drawer.draw_row("#", color=self.drawer.color_hash_tag)
                            self.draw_marked_string(tag,
                                                    filter_tag,
                                                    index_sub_str=index_tag,
                                                    color_default=background_color,
                                                    color_marked=self.drawer.color_search)
                            found = True
                            break
                if not found:
                    unmatched_tags.append(tag)

            # description
            unmatched_description = True

            # get a matched word in the description
            if len(desc) == 0:
                unmatched_description = False
            elif filter_desc is not None and (filter_desc != "" or filter_tags == []):
                res = self._get_matching_word_from_sentence(desc, filter_desc)
                if res is not None:
                    start = res[0]
                    middle = res[1]
                    end = res[2]

                    # @ + word + space
                    self.drawer.draw_row(" ", color=background_color)
                    self.drawer.draw_row("@", color=self.drawer.color_hash_tag)
                    # print the start of the matched work
                    self.drawer.draw_row(start, color=background_color)
                    # print the search string
                    self.drawer.draw_row(middle, color=self.drawer.color_search)
                    # print the end of the matched word
                    self.drawer.draw_row(end, color=background_color)
                    unmatched_description = False

            # print not matched tags
            for tag in unmatched_tags:
                self.drawer.draw_row(" ", color=background_color)
                self.drawer.draw_row("#", color=self.drawer.color_hash_tag)
                self.drawer.draw_row(tag, color=background_color)

            # print not matching description
            if unmatched_description:
                self.drawer.draw_row(" ", color=background_color)
                self.drawer.draw_row("@", color=self.drawer.color_hash_tag)
                self.drawer.draw_row(desc, color=background_color)

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

    def _draw_help_line_selector(self):
        self.drawer.set_y(self.drawer.get_max_y() - 1)
        self.drawer.draw_row("Enter", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Select", x_indent=1)

        self.drawer.draw_row("<-|->", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Scroll", x_indent=1)

        self.drawer.draw_row("Tab", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("More", x_indent=1)

        self.drawer.draw_row("Canc", x_indent=2, color=self.drawer.color_columns_title)
        self.drawer.draw_row("Delete", x_indent=1)

    def _get_matching_word_from_sentence(self, sentence, search):
        """
        Search a string in a sentence and return the entire matching word
        NOTE: currently only the first match is return

        Given "hello how are you\nfine" and "" it returns ["hello how are you\nfine","", ""]
        Given "hello how are you\nfine" and "are" it returns ["","are", ""]
        Given "hello how are you\nfine" and "el" it returns ["h","el",lo"]
        Given "hello how are you\nfine" and "error" it returns None
        :param sentence:    sentence
        :param search:      string to search
        :return:            None if nothing found or a list strutted as explained in the description
        """

        start_word = 0
        end_word = len(sentence)
        search_len = len(search)

        if search_len == 0:
            return [sentence, "", ""]

        index_sub = sentence.lower().find(search)
        if index_sub != -1:
            # from the start of string to the start of the sub string
            for i in range(index_sub):
                if sentence[index_sub - i] == " " \
                        or sentence[index_sub - i] == "\n" \
                        or sentence[index_sub - i] == "\r" \
                        or sentence[index_sub - i] == "\t":
                    start_word = index_sub - i + 1
                    break
            # for sub string end to the end of the string
            for i in range(len(sentence) - (index_sub + search_len)):
                if sentence[index_sub + search_len + i] == " " \
                        or sentence[index_sub + search_len + i] == "\n" \
                        or sentence[index_sub + search_len + i] == "\r" \
                        or sentence[index_sub + search_len + i] == "\t":
                    end_word = index_sub + search_len + i
                    break

            return [
                sentence[start_word:index_sub],
                sentence[index_sub:index_sub + len(search)],
                sentence[index_sub + len(search):end_word]
            ]
        else:
            return None