import inspect
import logging
import sys
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
        to run this test check if the command's flag are retrieved correctly from the man page

        input:
            [[linux-only], [command, flag], [possible_result1, possible_result2, ..]]

        possible_result_x is needed because different system may have different man pages

        note: in the github action the following system have been tested:
            Ubuntu-16.04, Ubuntu-18.04, macOS-10.15

        :return:
        """
        parser = ManParser()
        all_true = True

        test_string = [
            [False, ["tar", "-C"], ["-C, --directory=DIR",
                                    "-C, --directory DIR",
                                    "-C directory, --cd directory, --directory directory"]],
            [False, ["tar", "-z"], ["-z, --gzip, --gunzip, --ungzip",
                                    "-z, --gzip, --gunzip --ungzip",
                                    "-z, --gunzip, --gzip"]],
            [False, ["tar", "-f"], ["-f, --file=ARCHIVE",
                                    "-f, --file ARCHIVE",
                                    "-f file, --file file"]],  # flag with special indexing
            [False, ["tar", "-v"], ["-v, --verbose",
                                    "-v  Produce verbose output.  In create and extract modes, tar will list each file name as"]],
            [True, ["tar", "--check-device"], ["--check-device"]],
            [False, ["ls", "-l"], ["-l     use a long listing format",
                                   "-l      (The lowercase letter ``ell''.)  List in long format.  (See"]],
            [False, ["netstat", "-a"], ["-a, --all",
                                        "-a    With the default display, show the state of all sockets; normally"]],  # this has a shorter space in front of the command
            [False, ["netstat", "-n"], ["--numeric, -n",
                                        "--numeric , -n",
                                        "-n    Show network addresses as numbers (normally netstat interprets"]],
            [False, ["netstat", "-v"], ["--verbose, -v",
                                        "--verbose , -v",
                                        "-v    Increase verbosity level."]],
            [True, ["netstat", "--verbose"], ["--verbose, -v",
                                              "--verbose , -v"]],
            [True, ["netstat", "--interfaces"], ["--interfaces, -i"]],  # outside the options chapter
            [False, ["lsof", "-i"], ["-i [i]   selects  the  listing  of  files any of whose Internet address",
                                     "-i [i]   selects the listing of files any of whose Internet address matches the address speci‐",
                                     "-i [i]   selects  the listing of files any of whose Internet address matches the address specified in i.  If no address is specified, this option selects the listing of all Internet and x.25 (HP-UX)"]],  # this man page contains 2 sentences which start with '-i'
            [False, ["wget", "--quiet"], ["-q"]],  # -q\n--quite
            [False, ["git", "--help"], ["--help"]],
            [False, ["git", "--version"], ["--version"]],
            [False, ["nmap", "-p"], ["-p port ranges (Only scan specified ports)",
                                     "-p port ranges (Only scan specified ports) ."]],
            [False, ["nmap", "-sC"], ["-sC",
                                      "-sC ."]],
            [False, ["nmap", "-sN"], ["-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)",
                                      "-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans) ."]],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
            [False, ["nmap", "-sF"], ["-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)",
                                      "-sN; -sF; -sX (TCP NULL, FIN, and Xmas scans) ."]],  # -sN; -sF; -sX (TCP NULL, FIN, and Xmas scans)
        ]
        for t in test_string:
            logging.info("input: " + str(t[1]))
            if not t[0] or sys.platform.startswith('linux'):
                if parser.load_man_page(t[1][0]):
                    flag_meaning = parser.get_flag_meaning(t[1][1])
                    if flag_meaning != None:
                        found = False
                        for meaning in t[2]:
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
                    print("warning! this command may not be available in your system:" + t[1])
                    logging.warning("warning! program not found in your system:" + t[1])
                    all_true = False
            else:
                logging.info("check skipped")

        if all_true:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

