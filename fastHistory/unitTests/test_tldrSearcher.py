import logging

from unittest import TestCase

from fastHistory.tldr.tldrSearcher import TLDRSearcher
from fastHistory.unitTests.loggerTest import LoggerTest


class TestTLDRSearcher(TestCase):
    """
    test class for the tldr searcher

    """

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

    def test_load_man_page(self):
        """
        get the meaning ('name' field) from the man page
        :return:
        """
        searcher = TLDRSearcher()

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
            i = 0
            for i in range(len(results)):
                if results[i][3].endswith(test[1] + ".md"):
                    found = True
                    break

            if test[2] > 0:
                self.assertTrue(len(results) > 0, msg="no results, check the 'pages' folder")
                self.assertTrue(found, msg="expected cmd is not within the results: %s" % test)
                self.assertTrue(i < test[2], msg="the cmd index is %s, expected: %s" % (i, test))
            else:
                self.assertTrue(len(results) == 0)


