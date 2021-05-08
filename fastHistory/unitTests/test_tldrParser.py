import logging
import time
from unittest import TestCase

from fastHistory.parser.InputData import InputData
from fastHistory.parser.inputParser import InputParser
from fastHistory.tldr.tldrParser import TLDRParser, ParsedTLDRExample
from fastHistory.tldr.tldrParserThread import TLDRParseThread
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
            [InputData(False, "randomstringwithnomatch", ["randomstringwithnomatch"]), "", 0],
            [InputData(False, "hex", ["hex"]), "hexdump", 3],
            [InputData(False, "srm", ["srm"]), "srm", 1],
            [InputData(False, "open port listen", ["open", "port", "listen"]), "netstat", 3],
            [InputData(False, "time boot", ["time", "boot"]), "systemd-analyze", 4],
            [InputData(False, "tar", ["tar"]), "tar", 1],  # tar is also a substring of many other cmds
            [InputData(False, "extract file gz", ["extract", "file", "gz"]), "tar", 1],  # "e[x]tract" string special case
            [InputData(False, "bios info", ["bios", "info"]), "dmidecode", 1],
            [InputData(False, "dns reverse", ["dns", "reverse"]), "drill", 3],
            [InputData(False, "keyboard layout", ["keyboard", "layout"]), "setxkbmap", 1]  # single result
        ]

        for test in test_strings:
            results = searcher.find_match_command(test[0])
            # check if the expected cmd is within the first x results
            found = False
            i = 0
            for i in range(len(results)):
                if results[i][TLDRParser.INDEX_TLDR_MATCH_CMD].endswith(test[1]):
                    found = True
                    break

            if test[2] > 0:
                self.assertTrue(len(results) > 0, msg="no results, check if the 'pages' folder exist")
                self.assertTrue(found, msg="expected cmd is not in the results: %s" % test)
                self.assertTrue(i < test[2], msg="the cmd index is %s, expected: %s" % (i, test))
            else:
                self.assertTrue(len(results) == 0)

    def test_TLDR_empty_input(self):
        searcher = TLDRParser()
        empty_input = InputData(False, "", [])
        results = searcher.find_match_command(empty_input)
        count_results = len(results)
        self.assertTrue(count_results > 100, msg="results are less then 100: %s" % count_results)

    def test_TLDR_search_time(self):
        searcher = TLDRParser()

        test_strings = [
            # input, excepted cmd, max index of expected cmd
            InputData(False, "", []),
            InputData(False, "randomstringwithnomatch", ["randomstringwithnomatch"]),
            InputData(False, "open port listen", ["open", "port", "listen"])
        ]

        for test in test_strings:
            start_time = time.time()
            results = searcher.find_match_command(test)
            execution_time = (time.time() - start_time)
            logging.info("execution_time: %s seconds" % execution_time)
            self.assertTrue(execution_time < 0.5, msg="execution takes too long: %s sec" % execution_time)

    def test_TLDR_search_with_simulated_manual_input(self):
        """
        note:
            without "thread.has_been_stopped()" check ->  >= 3 seconds
            with "thread.has_been_stopped()" check at fnames level -> 0.9 seconds
            with "thread.has_been_stopped()" check at line level -> 0.85 seconds
        :return:
        """

        test_strings = [
            "open port listen",
            "a fi le file ile"
        ]

        for test in test_strings:
            start_time = time.time()

            fake_manual_input = ""
            tldr_parser_thread = None
            tldr_parser = TLDRParser()
            for c in test:
                fake_manual_input += c
                input_data = InputParser.parse_input(test, is_search_mode=True)
                if tldr_parser_thread:
                    tldr_parser_thread.stop()
                tldr_parser_thread = TLDRParseThread(tldr_parser, input_data)
                tldr_parser_thread.start()
                time.sleep(0.05)

            while tldr_parser_thread.is_alive():
                time.sleep(0.01)

            execution_time = (time.time() - start_time)
            logging.info("execution_time: %s -> %s seconds" % (test, execution_time))
            self.assertTrue(execution_time < 3.0, msg="execution takes too long: %s sec" % execution_time)

    def test_TLDR_parser(self):
        searcher = TLDRParser()

        test_strings = [
            # input, excepted first example cmd, number of example
            # NOTE: this values may change with new dataset
            [InputData(False, "gunzip archive", ["gunzip", "archive"]), "gunzip {{archive.tar.gz}}", 3],
            [InputData(False, "apk update", ["apk", "update"]), "apk update", 6]
        ]

        for test in test_strings:
            logging.debug("input test: %s" % test)
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
