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
            ["randomstringwithnomatch", "", 0],
            ["process", "ps", 2],  # TODO improve this
            ["process list", "ps", 2],
            ["process list", "ps", 2],
            ["merge pdf page", "pdftk", 2],
            ["locate program", "which", 1],
            ["git diff", "git-diff", 2],
            ["hex", "hexdump", 3],
            ["srm", "srm", 1],
            ["open port listen", "netstat", 2],
            ["time boot", "uptime", 1],
            ["time boot", "systemd-analyze", 4],
            ["tar", "tar", 1],  # tar is also a substring of many other cmds
            ["extract file gz", "tar", 1],  # "e[x]tract" string special case
            ["bios info", "dmidecode", 1],
            ["dns reverse", "drill", 2],
            ["open default", "xdg-open", 1],
            ["download file", "wget", 1],
            ["download file", "curl", 5],  # TODO improve this
            ["download package", "apt-get", 3],  # TODO improve this
            ["keyboard layout", "setxkbmap", 1],  # single result
            # security
            ["extract from binary", "binwalk", 1],
            ["secure disk overwrite", "sfill", 1],
            ["scan network", "arp-scan", 1],
            ["scan port script", "nmap", 1],
        ]

        for test in test_strings:
            input_array = test[0].split(" ")
            input_data = InputData(False,  test[0], input_array)

            results = searcher.find_match_command(input_data)
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
        """
        the first call load read from disk (excepted time ~0,08)
        the second and third use the cached memory (expected time ~0,01)
        #
        :return:
        """
        searcher = TLDRParser()

        test_strings = [
            # input, excepted cmd, max index of expected cmd
            ["", 0.5],  # disk
            ["randomstringwithnomatch", 0.05],  # memory
            ["open port listen", 0.05],  # memory
        ]

        for test in test_strings:
            input_array = test[0].split(" ")
            input_data = InputData(False,  test[0], input_array)
            start_time = time.time()
            results = searcher.find_match_command(input_data)
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
            # input: [ Input object, excepted first example cmd, expected url, number of example for the specific command]
            # NOTE: this values may change with new TLDR version
            ["process ps", "ps aux", None, 7],
            ["gunzip archive", "gunzip {{archive.tar.gz}}", "https://manned.org/gunzip" , 3],
            ["list directory permission", "ls -1", "https://www.gnu.org/software/coreutils/ls" , 7],
            ["apk update", "apk update", None, 6]
        ]

        for test in test_strings:
            logging.debug("input test: %s" % test)
            input_array = test[0].split(" ")
            input_data = InputData(False,  test[0], input_array)
            results = searcher.find_match_command(input_data)

            self.assertTrue(len(results) > 0, msg="no results, check if the 'pages' folder exist")
            first_result = results[0]
            parsed_tldr_example = searcher.get_tldr_cmd_examples(first_result)
            example_count = 0

            for row in parsed_tldr_example.get_rows():
                if row[ParsedTLDRExample.INDEX_EXAMPLE_TYPE] == ParsedTLDRExample.Type.EXAMPLE:
                    example_count += 1
                    if example_count == 0:
                        self.assertEqual(test[1], row[ParsedTLDRExample.INDEX_EXAMPLE_VALUE], msg="wrong command found: %s -> %s" % (test, row))
                        # this should get the same result as the previous assert
                        self.assertTrue(example_count, parsed_tldr_example.get_first_example_index())
                        self.assertEqual(test[1], parsed_tldr_example.get_current_selected_example(row_index=example_count), msg="wrong command found: %s -> %s" % (test, row))
                        # there are 2 rows until the next example
                        self.assertEqual(2, parsed_tldr_example.get_delta_next_example_index(example_count))
                        # because this is the first, the delta is 0
                        self.assertEqual(0, parsed_tldr_example.get_delta_previous_example_index(example_count))
            if test[2]:
                self.assertTrue(parsed_tldr_example.has_url_more_info(), msg="no url found: %s" % test)
            self.assertEqual(test[2], parsed_tldr_example.get_url_more_info(), msg="wrong url: %s" % test)
            self.assertLessEqual(test[3], example_count, msg="wrong number of command found: %s" % test)

    def test_format_tldr_pages(self):
        searcher = TLDRParser()
        self.assertRegex(searcher.format_tldr_pages(), "\d pages have been correctly formatted", msg="something wrong with TLDR pages, maybe the format has changed with a TLDR update")

