
from threading import Thread

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastHistory.parser.InputData import InputData
    from fastHistory.tldr.tldrParser import TLDRParser


class TLDRParseThread(Thread):

    def __init__(self, tldr_parser: "TLDRParser", user_data: "InputData"):
        Thread.__init__(self)
        self.tldr_parser = tldr_parser
        self.user_data = user_data
        self.result_tldr_options: list = []
        self.stopped = False

    def run(self):
        self.result_tldr_options = self.tldr_parser.find_match_command(self.user_data, self)

    def stop(self):
        self.stopped = True

    def has_been_stopped(self):
        return self.stopped

    def get_result_tldr_options(self) -> list:
        return self.result_tldr_options



