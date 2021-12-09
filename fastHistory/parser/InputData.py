

class InputData(object):
    def __init__(self, advanced: bool, main_str: str, command_words: list, description: str = None,
                 description_words: list = [], tags: list = []):
        self.advanced = advanced
        self.main_str = main_str
        self.main_words = command_words
        self.description = description
        self.description_words_strict = description_words
        self.tags_strict = tags
        self.description_words_complete = None
        self.tags_complete = None
        self.all_words = None

    def is_advanced(self) -> bool:
        return self.advanced

    def get_main_str(self) -> str:
        return self.main_str

    def get_main_words(self) -> list:
        return self.main_words

    def get_description_str(self) -> str:
        return self.description

    def get_description_words(self, strict=False) -> list:
        if strict:
            return self.description_words_strict
        else:
            if self.description_words_complete is None:
                self.description_words_complete = list(set(self.main_words + self.description_words_strict))
            return self.description_words_complete

    def get_tags(self, strict=False) -> list:
        if strict:
            return self.tags_strict
        else:
            if self.tags_complete is None:
                self.tags_complete = list(set(self.main_words + self.tags_strict))
            return self.tags_complete

    def get_all_words(self) -> list:
        if self.all_words is None:
            l_new = []
            l_old_with_duplicates = self.main_words + self.tags_strict + self.description_words_strict
            for item in l_old_with_duplicates:
                if item not in l_new:
                    l_new.append(item)
            self.all_words = l_new
        return self.all_words
