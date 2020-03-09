import logging
from unittest import TestCase

import os

from fastHistory.parser.inputParser import InputParser
from fastHistory.unitTests.loggerTest import LoggerTest


class TestInputParser(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

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
            res = InputParser.parse_input(test[0], is_search_cmd=False)
            if test[1] is None:
                self.assertEqual(res, None)
            else:
                self.assertEqual(res.get_main_str(), test[1][0])
                if res.is_advanced():
                    self.assertEqual(res.get_description_str(), test[1][1])
                    self.assertEqual(res.get_tags(strict=True), test[1][2])

    def test_parse_cmd_search(self):
        """
        test different combination of user input with tags and description
        the test is successful if the returned array match the expected one

        :return:
        """
        # [test, result]
        test_cases = [
            ["ls -la", ["ls -la", None, []]],
            ["ls -ll #", ["ls -ll", None, [""]]],
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
            res = InputParser.parse_input(test[0], is_search_cmd=True)
            self.assertEqual(res.get_main_str(), test[1][0])
            if res.is_advanced():
                self.assertEqual(res.get_description_str(), test[1][1])
                self.assertEqual(res.get_tags(strict=True), test[1][2])

    def test_parse_cmd_search_words(self):
        """
        test different combination of user input with tags and description
        the test is successful if the returned array match the expected one

        :return:
        """
        # [test, result]
        test_cases = [
            ["aa #aa @aa", [["aa"], ["aa"], ["aa"]]],
            ["ls -la", [["ls", "-la"], [], []]],
            ["ls -ll #", [["ls", "-ll"], [], [""]]],
            ["ls -la # #", [["ls", "-la"], [], ["", ""]]],
            ["ls -la @", [["ls", "-la"], [""], []]],
            ["ls -la #1", [["ls", "-la"], [], ["1"]]],
            ["ls -la #1 #2 #3 @desc", [["ls", "-la"], ["desc"], ["1", "2", "3"]]],

            ["ls -la #2 words @3 words !", [["ls", "-la"], ["3", "words", "!"], ["2 words"]]],
            ["echo 2 ", [["echo", "2"], [], []]],
            [" echo 2  ",  [["echo", "2"], [], []]],

            ["#allowed", [[""], [], ["allowed"]]],
            [" #allowed", [[""], [], ["allowed"]]],
            ["@allowed", [[""], ["allowed"], []]],
            [" @allowed", [[""], ["allowed"], []]],

            ["#", [[""], [], [""]]],
            ["@", [[""], [""], []]]
        ]

        for test in test_cases:
            res = InputParser.parse_input(test[0], is_search_cmd=True)
            self.assertEqual(res.get_main_words(), test[1][0])
            if res.is_advanced():
                self.assertEqual(res.get_description_words(strict=True), test[1][1])
                self.assertEqual(sorted(res.get_description_words(strict=False)), sorted(set(test[1][0] + test[1][1])))
                self.assertEqual(res.get_tags(strict=True), test[1][2])
                self.assertEqual(sorted(res.get_tags(strict=False)), sorted(set(test[1][0] + test[1][2])))

    def test_input_validation_edit_tags(self):
        """
        test tags input validation parser

        :return:
        """
        # [test, result]
        test_cases = [
            ["", []],
            ["#", [""]],
            ["#tag1", ["tag1"]],
            [" # tag1 ", ["tag1"]],
            ["#tag1 #tag2", ["tag1", "tag2"]],
            ["#tag1 #tag2 #tag2", ["tag1", "tag2", "tag2"]],
            ["#tag1  #tag2      #tag2", ["tag1", "tag2", "tag2"]],
            ["#some_special-char_is_allowed", ["some_special-char_is_allowed"]],
            ["#spaces are also   allowed", ["spaces are also   allowed"]],
            ["##", ["", ""]],  # TODO improve
            ["#hello?%", None],
            ["#@", None]
        ]

        for test in test_cases:
            res = InputParser.parse_tags_str(test[0])
            self.assertEqual(test[1], res)

    def test_input_validation_edit_description(self):
        """
        test description input validation parser

        :return:
        """
        # [test, result]
        test_cases = [
            ["", ""],
            ["@", ""],
            ["@description", "description"],
            ["@-_.,!?\t :;%+()=", "-_.,!?\t :;%+()="],
            ["@#notvalid", None],
            [" @to-trim ", "to-trim"]
        ]

        for test in test_cases:
            res = InputParser.parse_description(test[0])
            self.assertEqual(test[1], res)
