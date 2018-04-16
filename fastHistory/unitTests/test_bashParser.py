from unittest import TestCase

from parser import bashlex, bashParser


class TestBashParser(TestCase):
    """
    test class for the bash parser
    """

    def test_parse(self):
        self.parser = bashParser.BashParser()
        test_list = [
            ["ls -a -b -l; ls -a -v ",                  [[['ls', None], [['-a', None], ['-b', None], ['-l', None], ['-v', None]]]]],
            ["sudo blkid -trv | grep swap -r",          [[['blkid', None], [['-trv', None]]], [['grep', None], [['swap', None], ['-r', None]]]]],
            ["srm -lsv /media/cecss/  # comment",       [[['srm', None], [['-lsv', None], ['/media/cecss/', None]]]]],
            ['cat "$(ls)" -v',                          [[['cat', None], [['$(ls)', None], ['-v', None]]]]],
            ['while true; do lsof /path/to/file; done;', [[['lsof', None], [['/path/to/file', None]]]]]
        ]

        for test in test_list:
            result = list()
            cmd_parsed = bashlex.parse(test[0])
            self.parser.get_flags_from_bash_node(cmd_parsed, result)
            self.assertEqual(result, test[1])

    def test_parse_quote_cmd(self):
        self.parser = bashParser.BashParser()
        test_list = [
            "sudo blkid -trv | grep swap -r",
            "echo 'sdsd'"
        ]

        for res in test_list:
            # TODO complete
            pass

    def test_decompose_possible_concatenated_flags(self):
        res = bashParser.BashParser.decompose_possible_concatenated_flags("-lsv")
        self.assertEqual(res, ['-l', '-s', '-v'])

        res = bashParser.BashParser.decompose_possible_concatenated_flags("-l")
        self.assertEqual(res, ['-l'])

        res = bashParser.BashParser.decompose_possible_concatenated_flags("notAFlag")
        self.assertEqual(res, [])


