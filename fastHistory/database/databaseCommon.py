

class DatabaseCommon:

    @staticmethod
    def get_all_unique_combinations(string_array):
        """
        split the given string into a set of word and return an array of tuples with all possible word combinations
        note: above 4 words the given order is the only one returned to avoid performance issues

        :param string_array: e.g. ["git", "commit"]
        :return:             e.g. [("git","commit"),("commit","git")]
        """
        if string_array is not None:
            return list(DatabaseCommon._unique_permutations(string_array))
        else:
            return None

    @staticmethod
    def _unique_permutations(elements):
        """
        get all unique element order combination

        :param elements:    array of words
        :return:
        """
        if len(elements) == 1:
            yield (elements[0],)
        else:
            unique_elements = set(elements)
            for first_element in unique_elements:
                remaining_elements = list(elements)
                remaining_elements.remove(first_element)
                for sub_permutation in DatabaseCommon._unique_permutations(remaining_elements):
                    yield (first_element,) + sub_permutation

    @staticmethod
    def cast_return_type(data):
        """
        change the tags return type from string to array
        :param data:
        :return:
        """
        new_data = []
        for i in range(len(data)):
            tags_str = data[i][2]
            tags = tags_str.split("#")
            # remove first empty item
            if len(tags) > 0 and tags[0] == "":
                tags = tags[1:]
            new_data.append([data[i][0], data[i][1], tags])
        return new_data
