

class Input(object):
    def __init__(self, advanced, command_str, command_words, description=None, description_words=[], tags=[]):
        self.advanced = advanced
        self.main_str = command_str
        self.main_words = command_words
        self.description = description
        self.description_words_strict = description_words
        self.description_words_complete = list(set(self.main_words + self.description_words_strict))
        self.tags_strict = tags
        self.tags_complete = list(set(self.main_words + self.tags_strict))

    def is_advanced(self):
        return self.advanced

    def get_main_str(self):
        return self.main_str

    def get_main_words(self):
        return self.main_words

    def get_description_str(self):
        return self.description

    def get_description_words(self, strict=False):
        if strict:
            return self.description_words_strict
        else:
            return self.description_words_complete

    def get_tags(self, strict=False):
        if strict:
            return self.tags_strict
        else:
            return self.tags_complete
