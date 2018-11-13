

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

    def draw_marked_string(self, text, sub_str, index_sub_str=None, color_default=1, color_marked=None,
                           case_sensitive=False, recursive=True):
        """
        given a string and a sub string it will print the string with the sub string of a different color

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

    def draw_option(self, cmd, tags, desc, filter_cmd, filter_desc, filter_tags, context_shift,
                    last_column_size=0, selected=False):
        """
        draw one option line

        :param cmd:                 bash command
        :param tags:                tags
        :param desc:                description
        :param filter_cmd:          string used to filter cmd
        :param filter_desc:         string used to filter description (in default search it is the same of filter_cmd)
        :param filter_tags:         string used to filter tags (in default search it is the same of filter_cmd)
        :param context_shift:       context shift obj   # TODO make this an obj variable
        :param last_column_size:    tag and description column size
        :param selected:            if True the option is selected and underlined
        :return:
        """
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
        cmd = context_shift.get_text_shifted(cmd, max_x=self.drawer.max_x - last_column_size - 4)
        self.draw_marked_string(cmd, filter_cmd, color_marked=self.drawer.color_search, color_default=background_color)

        if last_column_size:
            # tag and description section
            self.drawer.set_x(self.drawer.max_x - last_column_size - 1)

            # print matched tags
            unmatched_tags = []
            for tag in tags:
                found = False
                for filter_tag in filter_tags:
                    if filter_tag != "":
                        index_tag = tag.lower().find(filter_tag)
                        if index_tag != -1:
                            self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                            if selected:
                                self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag_selected)
                            else:
                                self.drawer.draw_row(self.CHAR_TAG, color=self.drawer.color_hash_tag)

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
                    self.drawer.draw_row(self.CHAR_SPACE, color=background_color)
                    if selected:
                        self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag_selected)
                    else:
                        self.drawer.draw_row(self.CHAR_DESCRIPTION, color=self.drawer.color_hash_tag)
                    # print the start of the matched work
                    self.drawer.draw_row(start, color=background_color)
                    # print the search string
                    self.drawer.draw_row(middle, color=self.drawer.color_search)
                    # print the end of the matched word
                    self.drawer.draw_row(end, color=background_color)
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
