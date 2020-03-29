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

        [[command, flag], [possible_result1, possible_result2, ..]]

        possible_result_x is needed because different system may have different man pages

        :return:
        """
        parser = ManParser()
        all_true = True

        test_string = [
            [["tar", "-C"], ["-C, --directory=DIR", "-C directory"]],
            [["tar", "-z"], ["-z, --gzip, --gunzip, --ungzip",  "-z  (c mode only) Compress the resulting archive with gzip(1)."]],
            [["tar", "-f"], ["-f, --file=ARCHIVE", "-f file"]],  # flag with special indexing
            [["tar", "-v"], ["-v, --verbose", "-v  Produce verbose output.  In create and extract modes, tar will list each file name as"]],
            [["tar", "--check-device"], ["--check-device"]],
            [["ls", "-l"], ["-l     use a long listing format"]],
            [["netstat", "-a"], ["-a, --all"]],  # this has a shorter space in front of the command
            [["netstat", "-n"], ["--numeric, -n"]],
            [["netstat", "-v"], ["--verbose, -v"]],
            [["netstat", "--interfaces"], ["--interfaces, -i"]],  # outside the options chapter
            [["netstat", "--verbose"], ["--verbose, -v"]],
            [["lsof", "-i"], ["-i [i]   selects  the  listing  of  files any of whose Internet address"]],  # this man page contains 2 sentences which start with '-i'
            [["wget", "--quiet"], ["-q"]],  # -q\n--quite
            [["git", "--help"], ["--help"]],
            [["git", "--version"], ["--version"]],
            [["nmap", "-p"], ["-p port ranges (Only scan specified ports)"]],
            [["nmap", "-sC"], ["-sC"]],
            [["nmap", "-sN"], ["-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)"]],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
            [["nmap", "-sF"], ["-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)"]],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
        ]
        for t in test_string:
            logging.info("test input: " + str(t[0]))
            if parser.load_man_page(t[0][0]):
                flag_meaning = parser.get_flag_meaning(t[0][1])
                if flag_meaning != None:
                    found = False
                    for meaning in t[1]:
                        if flag_meaning[0][1] == meaning:
                            found = True
                            break
                    if not found:
                        logging.info("flag meaning does not match any possible solution: '%s'" % flag_meaning[0][1])
                        logging.info("full flag: '%s'" % flag_meaning)
                        all_true = False
                else:
                    logging.error("flag not found, please investigate with the following man output")
                    logging.debug(parser.get_man_page())
                    all_true = False
            else:
                print("warning! this command may not be available in your system:" + t[0])
                logging.warning("warning! program not found in your system:" + t[0])
                all_true = False

        if all_true:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

