import inspect
import logging
from unittest import TestCase

import os

from fastHistory.parser.manParser import ManParser
from fastHistory.unitTests.loggerTest import LoggerTest


class TestManParser(TestCase):
    """
    test class for the man parser
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
        parser = ManParser()

        dir_path = os.path.dirname(os.path.realpath(__file__))

        test_strings = [
            ["tar", True],
            ["ls", True],
            ["netstat", True],
            ["non-existing-cmd", False],  # this will throw a process error
            [dir_path + "/" + "adb_test_file", False]  # this will throw a timeout error (note that this file will not be published on git)
        ]

        for t in test_strings:
            if t[1]:
                self.assertTrue(parser.load_man_page(t[0]))
            else:
                self.assertFalse(parser.load_man_page(t[0]))
            meaning = parser.get_cmd_meaning()
            if t[1]:
                self.assertIsNotNone(meaning)
            else:
                self.assertIsNone(meaning)

    def test_get_cmd_meaning(self):
        parser = ManParser()

        test_string = [
            "tar",
            "ls",
            "netstat",
            "wget",
            "grep",
            "nmap"
        ]
        for t in test_string:
            logging.info("test: " + str(t))
            self.assertTrue(parser.load_man_page(t))
            meaning = parser.get_cmd_meaning()
            self.assertTrue(meaning)
            logging.info(meaning)

    def test_get_flag_meaning(self):
        """
        to run this test check if all commands are available in your system

        :return:
        """
        parser = ManParser()

        test_string = [
            # ["tar", "-d"], # disabled because macOS has a different tar utility
            ["ls", "-l"],
            ["netstat", "-a"],
            ["netstat", "-n"],
            ["lsof", "-i"],
            ["wget", "--quiet"],
            ["git", "--help"],
            ["git", "--version"],
            ["nmap", "-p"],
            ["nmap", "-sC"],
            ["nmap", "-sN"],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
            ["nmap", "-sF"],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
        ]
        for t in test_string:
            logging.info("test input: " + str(t))
            if parser.load_man_page(t[0]):
                flag_meaning = parser.get_flag_meaning(t[1])
                self.assertTrue(flag_meaning)
                logging.info("flag meaning: " + str(flag_meaning))
            else:
                print("warning! program not found in your system:" + t[0])
                logging.warning("warning! program not found in your system:" + t[0])
                self.assertTrue(False)


