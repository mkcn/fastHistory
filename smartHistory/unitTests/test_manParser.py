from unittest import TestCase

from parser.manParser import ManParser


class TestManParser(TestCase):
    """
    test class for the man parser
    """

    def test_load_man_page(self):
        parser = ManParser()

        test_string = [
            "tar",
            "ls"
        ]
        for t in test_string:
            self.assertTrue(parser.load_man_page(t))

    def test_get_cmd_meaning(self):
        parser = ManParser()

        test_string = [
            "tar"
        ]
        for t in test_string:
            self.assertTrue(parser.load_man_page(t))
            self.assertTrue(parser.get_cmd_meaning())

    def test_get_flag_meaning(self):
        parser = ManParser()

        test_string = [
            ["tar", "-d"],
            ["ls", "-l"]
        ]
        for t in test_string:
            self.assertTrue(parser.load_man_page(t[0]))
            self.assertTrue(parser.get_flag_meaning(t[1]))


