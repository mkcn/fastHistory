import logging
import time
from unittest import TestCase

from fastHistory.tldr.tldrParser import TLDRParser, ParsedTLDRExample
from fastHistory.unitTests.loggerTest import LoggerTest


class TestTLDRParser(TestCase):
    """
    test class for the tldr searcher

    """

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

    def test_TLDR_search(self):
        """
        get the meaning ('name' field) from the man page
        :return:
        """
        searcher = TLDRParser()

        test_strings = [
            # input, excepted cmd, max index of expected cmd
            [["randomstringwithnomatch"], "", 0],
            [["hex"], "hexdump", 3],
            [["open", "port", "listen"], "netstat", 3],
            [["time", "boot"], "systemd-analyze", 4],
            [["tar"], "tar", 1],  # tar is also a substring of many other cmds
            [["extract", "file", "gz"], "tar", 1],  # "e[x]tract" string special case
            [["bios", "info"], "dmidecode", 1],
            [["dns", "reverse"], "drill", 3],
            [["keyboard", "layout"], "setxkbmap", 1]  # single result
        ]

        for test in test_strings:
            results = searcher.find_match_command(test[0])
            # check if the expected cmd is within the first x results
            found = False
            cmd_to_draw_index = 1
            i = 0
            for i in range(len(results)):
                if results[i][cmd_to_draw_index].endswith(test[1]):
                    found = True
                    break

            if test[2] > 0:
                self.assertTrue(len(results) > 0, msg="no results, check if the 'pages' folder exist")
                self.assertTrue(found, msg="expected cmd is not within the results: %s" % test)
                self.assertTrue(i < test[2], msg="the cmd index is %s, expected: %s" % (i, test))
            else:
                self.assertTrue(len(results) == 0)

    def test_TLDR_search_time(self):
        searcher = TLDRParser()

        test_strings = [
            # input, excepted cmd, max index of expected cmd
            ["randomstringwithnomatch"],
            ["open", "port", "listen"],
        ]

        for test in test_strings:
            start_time = time.time()
            results = searcher.find_match_command(test)
            execution_time = (time.time() - start_time)
            logging.info("--- %s seconds ---" % execution_time)
            self.assertTrue(execution_time < 0.5, msg="execution takes too long")

    def test_TLDR_parser(self):
        searcher = TLDRParser()

        test_strings = [
            # input, excepted first example cmd, number of example
            # NOTE: this values may change with new dataset
            [["gunzip", "archive"], "gunzip {{archive.tar.gz}}", 3],
            [["apk", "update"], "apk update", 6]
        ]

        for test in test_strings:
            logging.debug("test: %s" % test)
            results = searcher.find_match_command(test[0])

            self.assertTrue(len(results) > 0, msg="no results, check if the 'pages' folder exist")
            first_result = results[0]
            parsed_tldr_example = searcher.get_tldr_cmd_examples(first_result)
            example_count = 0
            for row in parsed_tldr_example.get_rows():
                if row[ParsedTLDRExample.INDEX_EXAMPLE_TYPE] == ParsedTLDRExample.Type.EXAMPLE:
                    if example_count == 0:
                        self.assertEqual(test[1], row[ParsedTLDRExample.INDEX_EXAMPLE_VALUE], msg="wrong command found: %s -> %s" % (test, row))
                    example_count += 1
            self.assertEqual(test[2], example_count, msg="wrong number of command found")
