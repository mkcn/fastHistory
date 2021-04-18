import threading

from fastHistory.tldr.tldrParser import TLDRParser, ParsedTLDRExample


class TLDRParseThread(threading.Thread):

    def __init__(self, tldr_parser: TLDRParser, user_input: list, current_index: int):
        threading.Thread.__init__(self)
        self.tldr_parser = tldr_parser
        self.user_input = user_input
        self.current_index = current_index
        self.result_tldr_options: list = []
        self.stopped = False

    def run(self):
        self.result_tldr_options = self.tldr_parser.find_match_command(self.user_input, self)

    def stop(self):
        self.stopped = True

    def has_been_stopped(self):
        return self.stopped

    def get_result_tldr_options(self) -> list:
        return self.result_tldr_options



