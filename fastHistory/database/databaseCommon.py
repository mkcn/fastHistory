

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
