

class TextManager(object):
    """
    class to manager any input textbox generically

    this will take care of input text too long and it will shift it accordingly
    """
    TEXT_TOO_LONG = '…'

    text = None
    text_lower = None
    text_len = 0
    cursor_index = 0
    use_lower = False
    max_x = None

    def __init__(self, text="", use_lower=False, max_x=None, margin_x=0):
        self.text = text
        self.text_len = len(self.text)
        self.cursor_index = self.text_len
        self.use_lower = use_lower
        if self.use_lower:
            self.text_lower = text.lower()
        self.max_x = max_x
        self.margin_x = margin_x

    def delete_char(self):
        """
        delete one char if the search text is not empty and if cursor is not at the beginning

        :return: True is char was deleted, False otherwise
        """
        if self.text_len > 0 and self.cursor_index > 0:
            # delete char at the position of the cursor inside the search text field
            self.text = self.text[0:self.cursor_index - 1] + \
                               self.text[self.cursor_index:self.text_len]
            self.cursor_index -= 1
            self.text_len -= 1
            if self.use_lower:
                self.text_lower = self.text.lower()
            return True
        return False

    def add_string(self, string, forbidden_chars):
        """
        add char at the position of the cursor inside the text

        :param string: string to add, usually only a char but it could be a string or a unicode char
        :param forbidden_chars: array of chars not allowed
        :return:    true if successful, false otherwise
        """
        # remove special chars such as 'new line' and 'return carriage'
        for char in forbidden_chars:
            string = string.replace(char, '')
        # if python3 is not able to print the string then it will be shown as "\xNN" or "\uNNNN"
        if "\\x" in repr(string) or "\\u" in repr(string):
            return False

        # TODO add 'max' parameter and check input total len
        string_len = len(string)
        if string_len > 0:
            self.text = self.text[0:self.cursor_index] + \
                        string + \
                        self.text[self.cursor_index:self.text_len]
            self.cursor_index += string_len
            self.text_len += string_len
            if self.use_lower:
                self.text_lower = self.text.lower()
            return True
        return False

    def move_cursor_left(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1

    def move_cursor_right(self):
        if self.cursor_index < 1000:
            self.cursor_index += 1

    def move_cursor_to_end(self):
        self.cursor_index = self.text_len

    def move_cursor_to_start(self):
        self.cursor_index = 0

    def set_text(self, text):
        if self.text != text:
            text_len = len(text)
            self.cursor_index = text_len
            self.text_len = text_len
            self.text = text
            if self.use_lower:
                self.text_lower = self.text.lower()
            return True
        else:
            return False

    def set_max_x(self, max_x, with_margin_x=False):
        if with_margin_x:
            self.max_x = max_x - self.margin_x
        else:
            self.max_x = max_x

    def get_text(self):
        return self.text

    def _calculate_text_shifted(self, text, text_len, max_x, return_cursor_index=False):
        if max_x is None or text_len < max_x:
            # |-----x--  |
            # |x-------  |
            # |-------x  |
            if return_cursor_index:
                return self.cursor_index
            return text
        else:
            # |--------x-|.--
            # |---------x|.--
            if self.cursor_index < max_x:
                if return_cursor_index:
                    return self.cursor_index
                else:
                    return text[:max_x] + self.TEXT_TOO_LONG
            # --|.---------x|
            elif self.cursor_index >= max_x and self.cursor_index == text_len:
                if return_cursor_index:
                    return max_x
                else:
                    # +1 is to print the "TEXT_TOO_LONG"
                    return self.TEXT_TOO_LONG + text[self.cursor_index - max_x + len(self.TEXT_TOO_LONG):]
            # -|.---------x|.-
            else:
                if return_cursor_index:
                    return max_x
                else:
                    # +1 is to print the "TEXT_TOO_LONG"
                    return self.TEXT_TOO_LONG + text[
                                    self.cursor_index - max_x + len(self.TEXT_TOO_LONG):self.cursor_index] + self.TEXT_TOO_LONG

    def get_text_to_print(self):
        return self._calculate_text_shifted(self.text, self.text_len, self.max_x)

    def get_cursor_index_to_print(self):
        return self._calculate_text_shifted(self.text, self.text_len, self.max_x, return_cursor_index=True)

    def get_text_lower(self):
        return self.text_lower

    def get_text_len(self):
        return self.text_len

    def get_cursor_index(self):
        return self.cursor_index

    def is_cursor_at_the_end(self):
        return self.cursor_index == self.text_len

    def is_cursor_at_the_beginning(self):
        return self.cursor_index == 0


class ContextShifter(object):
    """
    class to manage the shift value which show the data from the db shifted

    e.g. "echo 'test'" shifted on left
         "..o 'test'"
    """

    def __init__(self):
        self.context_shift = 0

    def reset_context_shifted(self):
        self.context_shift = 0

    def is_context_index_zero(self):
        return self.context_shift == 0

    def shift_context_right(self):
        if self.context_shift < 1000:
            self.context_shift += 5

    def shift_context_left(self):
        if self.context_shift >= 5:
            self.context_shift -= 5

    def get_text_shifted(self, text, max_x):
        if self.context_shift > 0:
            text = TextManager.TEXT_TOO_LONG + text[self.context_shift + len(TextManager.TEXT_TOO_LONG):]

        text_len = len(text)
        if text_len <= max_x:
            return text
        else:
            return text[:max_x-len(TextManager.TEXT_TOO_LONG)] + TextManager.TEXT_TOO_LONG
