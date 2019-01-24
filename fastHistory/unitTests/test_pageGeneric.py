from unittest import TestCase

from pick.pageGeneric import PageGeneric


class TestPageGeneric(TestCase):

    def test_find_sections_to_mark(self):
        test_cases = [
            # string, array, result
            ["", [""], []],
            ["a", ["a"], [['a', True]]],
            ["abca", ["a"], [['a', True], ['bc', False], ['a', True]]],
            ["abca", ["a", "b"], [['ab', True], ['c', False], ['a', True]]],
            ["abca", ["a", "b"], [['ab', True], ['c', False], ['a', True]]],
            ["1234567", ["1234", "4567"], [['1234567', True]]],  #this could be improved to not allow overloaded words
            ["test to check", ["test"], [['test', True], [' to check', False]]],
            ["test to check", ["est"], [['t', False], ['est', True], [' to check', False]]],
            [" a b c", [""], [[" a b c", False]]],
            [" a b c", ["d"], [[" a b c", False]]]
        ]

        for item in test_cases:
            self.assertEqual(PageGeneric.find_sections_to_mark(item[0], item[1]), item[2])


