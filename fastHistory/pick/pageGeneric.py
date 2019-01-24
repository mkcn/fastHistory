import logging

from database.dataManager import DataManager
from pick.textManager import TextManager


class PageGeneric(object):
    """
    generic class used to draw different pages of the programs
    Inheritance graph:

        PageGeneric
            PageSelect
            PageInfo
                PageEditDescription
                PageEditTags
    """

    SELECTOR_START = ">"
    SELECTOR_END = "<"
    SELECTOR_NOT = " "

    CHAR_DESCRIPTION = "@"
    CHAR_TAG = "#"
    CHAR_SPACE = " "
    CHAR_EDIT = 'E'

    INDEX_SECTION_VALUE = 0
    INDEX_SECTION_IS_MARKED = 1

    def __init__(self, drawer):
        self.drawer = drawer

    def clean_page(self):
        """
        clean screen

        :return:
        """
        self.drawer.clear()
        self.drawer.reset()

    def refresh_page(self):
        """
        force screen to refresh

        :return:
        """
        self.drawer.refresh()

    def has_minimum_size(self):
        """
        # draw screen if screen has minimum size
        :return:    true if the console has at least the minimum size
        """
        return self.drawer.get_max_y() > 4 and self.drawer.get_max_x() > 40

    def draw_marked_array(self, text, arr_sub_str, index_sub_str=None, color_default=1, color_marked=None,
                           case_sensitive=False, recursive=True):
        self.drawer.draw_row(text, color=color_default)
        len_text = len(text)

        for sub_str in arr_sub_str:
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
                self.drawer.set_x(len_text)
                self.drawer.draw_row(x= text[index_sub_str:index_sub_str + len_sub_str], color=color_marked)

            self.drawer.draw_row()

    def draw_marked_string(self, text, words_to_mark, color_default=1, color_marked=None,
                           case_sensitive=False, recursive=True):
        """
        given a string and a sub string it will print the string with the sub string of a different color

        :param text:             string to print
        :param words_to_mark:    array of strings to print with a different color
        :param color_default:    default color
        :param color_marked:     color sub string
        :param case_sensitive:   case sensitive search
        :param recursive:        if False stop the search at the first match, if True search all matches recursively
        :return:
        """

        for section in self.find_sections_to_mark(text, words_to_mark, case_sensitive, recursive):
            if not section[self.INDEX_SECTION_IS_MARKED]:
                self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=color_default)
            else:
                self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=color_marked)

    def draw_option(self, option, search_filters, context_shift, last_column_size=0, selected=False):
        """
        draw selected option and highlight words match filters
        """

        cmd = option[DataManager.OPTION.INDEX_CMD]
        desc = option[DataManager.OPTION.INDEX_DESC]
        tags = option[DataManager.OPTION.INDEX_TAGS]
        if search_filters[DataManager.INPUT.INDEX_IS_ADVANCED]:
            filter_cmd = search_filters[DataManager.INPUT.INDEX_MAIN_WORDS]
            filter_desc = search_filters[DataManager.INPUT.INDEX_DESC_WORDS]
            filter_tags = search_filters[DataManager.INPUT.INDEX_TAGS]
        else:
            filter_cmd = search_filters[DataManager.INPUT.INDEX_MAIN_WORDS]
            filter_desc = search_filters[DataManager.INPUT.INDEX_MAIN_WORDS]
            filter_tags = search_filters[DataManager.INPUT.INDEX_MAIN_WORDS]

        self.drawer.new_line()

        # if this option is selected set a background color
        if selected:
            background_color = self.drawer.color_selected_row
            # draw a colored line for the selected option
            self.drawer.draw_row(self.CHAR_SPACE * (self.drawer.get_max_x()), color=background_color)
        else:
            background_color = self.drawer.NULL_COLOR

        # selector
        self.drawer.set_x(0)
        if selected:
            self.drawer.draw_row(self.SELECTOR_START, color=self.drawer.color_selector)
        else:
            self.drawer.draw_row(self.SELECTOR_NOT, color=background_color)
        self.drawer.draw_row(self.CHAR_SPACE, color=background_color)

        #  cmd section
        # TODO remove this shift from here to draw marked string
        cmd = context_shift.get_text_shifted(cmd, max_x=self.drawer.max_x - last_column_size - 4)
        self.draw_marked_string(cmd, filter_cmd, color_marked=self.drawer.color_search, color_default=background_color)

        if last_column_size:
            # print tag and description sections with following order:
            #  - matching tags
            #  - matching description
            #  - not matching tags
            #  - not matching description
            self.drawer.set_x(self.drawer.max_x - last_column_size - 1)

            # print matched tags
            unmatched_tags = []
            for tag in tags:
                sections = self.find_sections_to_mark(tag, filter_tags)
                # logging.debug("tag sections: " + str(sections))

                sections_len = len(sections)
                # if at least one filter tag matches
                if sections_len >= 2 or (sections_len == 1 and sections[0][self.INDEX_SECTION_IS_MARKED] == 1):
                    self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                    if selected:
                        self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag_selected)
                    else:
                        self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag)

                    for section in sections:
                        if not section[self.INDEX_SECTION_IS_MARKED]:
                            self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=background_color)
                        else:
                            self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=self.drawer.color_search)
                else:
                    unmatched_tags.append(tag)

            # description
            unmatched_description = True

            # get a matched word in the description
            if len(desc) == 0:
                unmatched_description = False
            elif filter_desc is not None:
                # TODO when "@" is searched, show description before tags
                sections = self.find_sections_to_mark(desc, filter_desc)
                # logging.debug("desc sections: " + str(sections))
                sections_len = len(sections)
                # if at least one filter tag matches
                if sections_len >= 2 or (sections_len == 1 and sections[0][self.INDEX_SECTION_IS_MARKED] == 1):
                    # @ + word + space
                    self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                    if selected:
                        self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag_selected)
                    else:
                        self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag)
                    for i in range(sections_len):
                        section = sections[i]
                        if section[self.INDEX_SECTION_IS_MARKED]:
                            self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=self.drawer.color_search)
                        else:
                            if i == 0:
                                not_marked_sections = section[self.INDEX_SECTION_VALUE].split(' ')
                                not_marked_sections_len = len(not_marked_sections)
                                if not_marked_sections_len == 1:
                                    self.drawer.draw_row(not_marked_sections[0], color=background_color)
                                else:
                                    self.drawer.draw_row(TextManager.TEXT_TOO_LONG, color=background_color)
                                    self.drawer.draw_row(not_marked_sections[-1], color=background_color)
                            else:
                                self.drawer.draw_row(section[self.INDEX_SECTION_VALUE], color=background_color)
                    unmatched_description = False

            # print not matched tags
            for tag in unmatched_tags:
                self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                if selected:
                    self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag_selected)
                else:
                    self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag)
                self.drawer.draw_row(tag, color=background_color)

            # print not matching description
            if unmatched_description:
                self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                if selected:
                    self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag_selected)
                else:
                    self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag)
                self.drawer.draw_row(desc, color=background_color)

    @staticmethod
    def find_sections_to_mark(string, words_to_mark, case_sensitive=False, recursive=True):
        """
        given a string and a set of words to mark it returns an array of sections that indicate
        which section of the string has to be marked

        :param string:          string to search and mark (e.g. "ls -la dir")
        :param words_to_mark:   array of words to mark (e.g. ["ls","dir"])
        :param case_sensitive:  if true the search is done in case sensitive mode
        :param recursive:       if true the search is recursive, if false each word to mark is searched only once
        :return:                array of section (e.g. [["ls ", True][" -la ", False],["dir", True]]
        """
        marked = 1
        not_marked = 0

        if not case_sensitive:
            string_lower = string.lower()
        else:
            string_lower = string
        string_len = len(string)
        map_mark = [0] * string_len
        sections = []

        if words_to_mark is None:
            return [[string, False]]

        for word in words_to_mark:
            word_len = len(word)
            index = string_lower.find(word)

            while word_len > 0 and index != -1:
                # set to 1 each char to mark
                for i in range(word_len):
                    map_mark[index + i] = 1
                index = string_lower.find(word, index+word_len)
                if not recursive:
                    break

        current_value = 0
        previous_index = 0
        for i in range(string_len):
            if map_mark[i] != current_value:
                current_value = map_mark[i]
                if previous_index != i:
                    # add to section substring with boolean to indicate if it is marked or not
                    # 0 INDEX_SECTION_VALUE
                    # 1 INDEX_SECTION_IS_MARKED
                    sections.append([string[previous_index:i], (current_value == not_marked)])
                    previous_index = i
        if previous_index != string_len:
            sections.append([string[previous_index:], current_value == marked])
        return sections

