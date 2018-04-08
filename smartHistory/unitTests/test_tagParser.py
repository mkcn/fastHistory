from unittest import TestCase

from parser.tagParser import TagParser


class TestTagParser(TestCase):
    def test_parse_cmd(self):
        """
        test different combination of user input with tags and description
        the test is successful if the returned array match the expected one

        :return:
        """
        # [test, result]
        test_cases = [
            ["ls -la #", ["ls -la", [], None]],
            ["ls -la #1", ["ls -la", ["1"], None]],
            ["ls -la #1#2", ["ls -la", ["1", "2"], None]],
            ["ls -la #1#2 #3 ", ["ls -la", ["1", "2", "3"], None]],
            ["ls -la #1#2 #3 @", ["ls -la", ["1", "2", "3"], ""]],
            ["ls -la #1#2 #3 @desc", ["ls -la", ["1", "2", "3"], "desc"]],
            ["ls -la #word-0 @desc-0", ["ls -la", ["word-0"], "desc-0"]],
            ["ls -la #òàùè#ÄẞÖÄ #é @special chars", ["ls -la", ["òàùè", "ÄẞÖÄ", "é"], "special chars"]],
            ["ls -la #@desc", ["ls -la", [], "desc"]],
            ["ls -la #@a desc, with other chars! ", ["ls -la", [], "a desc, with other chars!"]],
            ["echo \#toignore #1", ["echo \#toignore", ["1"], None]],
            ["echo '#toignore' #1 #2", ["echo '#toignore'", ["1", "2"], None]],
            ["echo 1", None],
            ["echo#error", None]
        ]

        for test in test_cases:
            res = TagParser.parse_cmd(test[0])
            self.assertEqual(test[1], res)
