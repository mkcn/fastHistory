import os
import unittest
import fastHistory
import sys

from fastHistory.console import colors
from fastHistory.unitTests.loggerTest import LoggerBashTest, LoggerTest


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()
        cls.output_file = cls.logger_test.get_test_folder() + "output.db"

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

        if os.path.isfile(self.output_file):
            os.remove(self.output_file)

    def test_call_version(self):
        logger_test = LoggerBashTest()
        # --from-installer is needed to skip some env check
        sys.argv = ["", "-v", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertEqual(console_logs[0][LoggerBashTest.INDEX_TYPE], LoggerBashTest.NONE)
        self.assertRegex(console_logs[0][LoggerBashTest.INDEX_VALUE], "^([0-9]+).([0-9]+).([0-9]+)$")

    def test_call_help(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "-h", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertRegex(console_logs[0][LoggerBashTest.INDEX_VALUE], "^Usage:")

    def test_call_add(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--add-explicit", "ls -ls #unittest", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertEqual(console_logs[0][LoggerBashTest.INDEX_VALUE], "new command:  ls -ls")
        self.assertEqual(console_logs[1][LoggerBashTest.INDEX_VALUE], "tags:         " + colors.Cyan + "#" + colors.Color_Off + "unittest ")

    def test_call_add_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--add-explicit", "ls -ls #@#@", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertEqual(len(console_logs), 0)

    def test_call_export_with_parameter_and_import(self):

        logger_test = LoggerBashTest()
        sys.argv = ["", "--export", self.output_file, "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertEqual(console_logs[1][LoggerBashTest.INDEX_VALUE], "database file exported")

        logger_test = LoggerBashTest()
        sys.argv = ["", "--import", self.output_file, "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertRegex(console_logs[1][LoggerBashTest.INDEX_VALUE], "import database: \d+ elements imported")

    def test_call_export_with_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--export", "%/", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertRegex(console_logs[1][LoggerBashTest.INDEX_VALUE], "^error: please check your log file:")

    def test_call_export_with_error_2(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--export", "/", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertRegex(console_logs[1][LoggerBashTest.INDEX_VALUE], "^error: output path cannot be a directory")

    def test_call_import_with_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--import", "not-existing-file.db", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        self.assertRegex(console_logs[1][LoggerBashTest.INDEX_VALUE], "^input file does not exist:")

    def test_call_setup(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--setup", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        # no msg with error
        for log in console_logs:
            self.assertNotEqual(console_logs[0][LoggerBashTest.INDEX_TYPE], LoggerBashTest.ERROR)
        # last message value
        self.assertRegex(console_logs[-1][LoggerBashTest.INDEX_VALUE], "^please restart your terminal")

    def test_call_setup_with_config_reader_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--setup",]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        # no msg with error
        for log in console_logs:
            self.assertNotEqual(console_logs[0][LoggerBashTest.INDEX_TYPE], LoggerBashTest.ERROR)
        # last message value
        self.assertRegex(console_logs[-1][LoggerBashTest.INDEX_VALUE], "^please restart your terminal")

    def test_call_config_with_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--config", "--from-installer"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        # last message value
        if len(console_logs) == 4:
            self.assertEqual(console_logs[1][LoggerBashTest.INDEX_TYPE], LoggerBashTest.ERROR)
            self.assertEqual(console_logs[1][LoggerBashTest.INDEX_VALUE], "your terminal does not support automatic input injection")
        elif len(console_logs) == 1:
            # note: this test may be successful if executed directly from the terminal
            # e.g. python3 -m unittest discover -s fastHistory/
            self.assertEqual(console_logs[0][LoggerBashTest.INDEX_VALUE], "to change the config file use the following injected command")
        else:
            self.assertTrue(False)

    def test_call_config_with_error_with_config_reader_error(self):
        logger_test = LoggerBashTest()
        sys.argv = ["", "--config"]
        fastHistory.f(logger_console=logger_test)
        console_logs = logger_test.get_console_logs()
        # last message value
        if len(console_logs) == 4:
            self.assertEqual(console_logs[1][LoggerBashTest.INDEX_TYPE], LoggerBashTest.ERROR)
            self.assertEqual(console_logs[1][LoggerBashTest.INDEX_VALUE], "your terminal does not support automatic input injection")
        elif len(console_logs) == 1:
            # note: this test may be successful if executed directly from the terminal
            # e.g. python3 -m unittest discover -s fastHistory/
            self.assertEqual(console_logs[0][LoggerBashTest.INDEX_VALUE], "to change the config file use the following injected command")
        else:
            self.assertTrue(False)