import logging
import os

import bashlex

from unittest import TestCase
from fastHistory.parser import bashParser
from fastHistory.unitTests.loggerTest import LoggerTest


class TestBashParser(TestCase):
    """
    test class for the bash parser
    """

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

    def test_parse(self):
        self.parser = bashParser.BashParser()
        test_list = [
            ["ls -a -b -l; ls -a -v ",                  [[['ls', None], [['-a', None], ['-b', None], ['-l', None], ['-v', None]]]]],
            ["sudo blkid -trv | grep swap -r",          [[['blkid', None], [['-trv', None]]], [['grep', None], [['swap', None], ['-r', None]]]]],
            ["srm -lsv /media/cecss/  # comment",       [[['srm', None], [['-lsv', None], ['/media/cecss/', None]]]]],
            ['cat "$(ls)" -v',                          [[['cat', None], [['$(ls)', None], ['-v', None]]]]],
            ['while true; do lsof /path/to/file; done;', [[['lsof', None], [['/path/to/file', None]]]]],
            ["echo -e '\e]8;;htts://twitter.com/\aTwitter link\e]8;;\a'",  [[['echo', None], [['-e', None], ['\\e]8;;htts://twitter.com/\x07Twitter link\\e]8;;\x07', None]]]]]  # this break regex engine
        ]

        for test in test_list:
            result = list()
            cmd_parsed = bashlex.parse(test[0])
            self.parser.get_flags_from_bash_node(cmd_parsed, result)
            self.assertEqual(result, test[1])

    def test_decompose_possible_concatenated_flags(self):
        res = bashParser.BashParser.decompose_possible_concatenated_flags("-lsv")
        self.assertEqual(res, ['-l', '-s', '-v'])

        # single flag
        res = bashParser.BashParser.decompose_possible_concatenated_flags("-l")
        self.assertEqual(res, ['-l'])

        # double flags
        res = bashParser.BashParser.decompose_possible_concatenated_flags("-ll")
        self.assertEqual(res, ['-l'])

        # flag that should not be decomposed
        res = bashParser.BashParser.decompose_possible_concatenated_flags("--help")
        self.assertEqual(res, [])

        # not a flag
        res = bashParser.BashParser.decompose_possible_concatenated_flags("notAFlag")
        self.assertEqual(res, [])

    def test_parse_load_data(self):
        self.parser = bashParser.BashParser()
        test_list = [
            ["ls -ls", True],
            ["sudo blkid -trv | grep swap -r", True],
            ["echo -e '\e]8;;htts://twitter.com/\aTwitter link\e]8;;\a'", True]
        ]

        for res in test_list:
            data = self.parser.load_data_for_info_from_man_page(res[0])
            self.assertNotEqual(data, None)
            self.assertEqual(data[0], res[1])
