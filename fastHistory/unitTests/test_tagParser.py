import logging
from unittest import TestCase

import os

from parser.tagParser import TagParser


class TestTagParser(TestCase):

    log_file_name = "data/test_tagParser.log"

    def setUp(self):
        """
        setup absolute log path and log level
        :return:
        """
        current_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
        self.log_path = current_path + self.log_file_name

        logging.basicConfig(filename=self.log_path, level=logging.DEBUG)

    def test_parse_cmd(self):
        """
        test different combination of user input with tags and description
        the test is successful if the returned array match the expected one

        :return:
        """
        # [test, result]
        test_cases = [
            ["ls -la #", ["ls -la", None, [""]]],
            ["ls -la #1", ["ls -la", None, ["1"]]],
            ["ls -la #1 #2", ["ls -la", None, ["1", "2"]]],
            ["ls -la #1 #2 #3 ", ["ls -la", None, ["1", "2", "3"]]],
            ["ls -la #1 #2 #3 @", ["ls -la", "", ["1", "2", "3"]]],
            ["ls -la #1 #2 #3 @desc", ["ls -la", "desc", ["1", "2", "3"]]],
            ["ls -la #word-0 @desc-0", ["ls -la", "desc-0", ["word-0"]]],
            ["ls -la #òàùè #ÄẞÖÄ #é @special chars", ["ls -la", "special chars", ["òàùè", "ÄẞÖÄ", "é"]]],
            ["ls -la # @desc", ["ls -la", "desc", [""]]],
            ["ls -la # @a desc, with other chars! ", ["ls -la", "a desc, with other chars!", [""]]],
            ["echo \#toignore #1", ["echo \#toignore", None, ["1"]]],
            ["echo '#toignore' #1 #2", ["echo '#toignore'", None, ["1", "2"]]],
            ["echo 1", None],
            ["echo#error", None],
            ["#notallowed", None],
            ["@notallowed", None],
            ["ls @notallowed", None]
        ]

        for test in test_cases:
            res = TagParser.parse_cmd(test[0])
            self.assertEqual(test[1], res)

    def test_parse_cmd_search(self):
        """
        test different combination of user input with tags and description
        the test is successful if the returned array match the expected one

        :return:
        """
        # [test, result]
        test_cases = [
            ["ls -la", ["ls -la", None, []]],
            ["ls -la #", ["ls -la", None, [""]]],
            ["ls -la # #", ["ls -la", None, ["", ""]]],
            ["ls -la @", ["ls -la", "", []]],
            ["ls -la #1", ["ls -la", None, ["1"]]],
            ["ls -la #1 #2", ["ls -la", None, ["1", "2"]]],
            ["ls -la #1 #2 #3 ", ["ls -la", None, ["1", "2", "3"]]],
            ["ls -la #1 #2 #3 @", ["ls -la", "", ["1", "2", "3"]]],
            ["ls -la #1 #2 #3 @desc", ["ls -la", "desc", ["1", "2", "3"]]],
            ["ls -la #word-0 @desc-0", ["ls -la", "desc-0", ["word-0"]]],
            ["ls -la #òàùè #ÄẞÖÄ #é @special chars", ["ls -la", "special chars", ["òàùè", "ÄẞÖÄ", "é"]]],
            ["echo 'ඐ 123 لْحُرُ' #unicode", ["echo 'ඐ 123 لْحُرُ'", None, ["unicode"]]],

            ["ls -la # @a desc, with other chars! ", ["ls -la", "a desc, with other chars!", [""]]],
            ["echo \#toignore #1", ["echo \#toignore", None, ["1"]]],
            ["echo '#toignore' #1 #2", ["echo '#toignore'", None, ["1", "2"]]],
            ["echo 1", ["echo 1", None, []]],
            ["echo 2 ", ["echo 2 ", None, []]],
            [" echo 2  ", [" echo 2  ", None, []]],
            ["echo#notag", ["echo#notag", None, []]],
            ["#allowed", ["", None, ["allowed"]]],
            [" #allowed", ["", None, ["allowed"]]],
            ["@allowed", ["", "allowed", []]],
            [" @allowed", ["", "allowed", []]],
            ["ls @allowed", ["ls", "allowed", []]],
            [" ls @allowed", [" ls", "allowed", []]],
            ["ls -la #@desc", ["ls -la #@desc", None, []]],
            ["#", ["", None, [""]]],
            ["@", ["", "", []]],
            ["@desc #tag", ["@desc", None, ["tag"]]]  # corner case when the order is not correct
        ]

        for test in test_cases:
            res = TagParser.parse_cmd(test[0], is_search_cmd=True)
            self.assertEqual(test[1], res)
