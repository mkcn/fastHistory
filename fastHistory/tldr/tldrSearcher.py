import os
from fastHistory.console.consoleUtils import ConsoleUtils


class TLDRSearcher(object):
    """
    Offline search of command from TLDR pages (source: https://github.com/tldr-pages/tldr)
    """

    FOLDER_TLDR_PAGES = "pages/"
    PAGE_CMD_TITLE_CHAR = "#"
    PAGE_CMD_DESC_CHAR = ">"
    PAGE_CMD_DESC_MORE_INFO_STR = "> More information"
    PAGE_EXAMPLE_CHAR = "`"
    PAGE_EXAMPLE_DESC_CHAR = "-"

    def __init__(self, enabled_os_folders=None):
        # TODO read from configuration or make dynamic based on OS ( enabled_os_folders: "linux", "windows", "osx"
        if enabled_os_folders is not None:
            self.enabled_os_folders = ["common"] + enabled_os_folders
        else:
            self.enabled_os_folders = ["common", "linux"]  # "windows", "osx",
        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/" + self.FOLDER_TLDR_PAGES

    def find_match_command(self, words):
        # NO empty, already trimmed
        words = [word.lower() for word in words]
        result = []
        for os_folder in self.enabled_os_folders:
            for root, dirs, fnames in os.walk(self.dir_path + os_folder):
                for fname in fnames:
                    words_dict = dict((word, 0) for word in words)
                    total_weight = 0
                    with open(os.path.join(root, fname)) as f:
                        for line in f:
                            for word in words:
                                if word in line.lower():
                                    first_char = line[0]
                                    if first_char == self.PAGE_CMD_TITLE_CHAR:
                                        # check if title matches (e.g. "# tar\n")
                                        if word == line[2:-1].strip().lower():
                                            weight = 10
                                        else:
                                            weight = 1
                                    elif first_char == self.PAGE_CMD_DESC_CHAR:
                                        if line.startswith(self.PAGE_CMD_DESC_MORE_INFO_STR):
                                            weight = 1
                                        else:
                                            weight = 4
                                    elif first_char == self.PAGE_EXAMPLE_CHAR:
                                        weight = 1
                                    elif first_char == self.PAGE_EXAMPLE_DESC_CHAR:
                                        weight = 1
                                    else:
                                        # ignore line without the correct format
                                        weight = 0
                                    words_dict[word] += 1
                                    total_weight += weight
                    if all(count > 0 for count in words_dict.values()):
                        cmd_name = fname.rstrip(".md")
                        if ConsoleUtils.is_cmd_available_on_this_machine(cmd_name):
                            result.append([total_weight, words_dict, True, os.path.join(root, fname)])
                        else:
                            result.append([total_weight, words_dict, False, os.path.join(root, fname)])

        result.sort(key=TLDRSearcher._find_match_command_sort_key, reverse=True)
        return result

    @staticmethod
    def _find_match_command_sort_key(arr):
        return arr[0]

    def parse_tld_page(self, path_tldr_page):
        # TODO complete
        with open(path_tldr_page) as f:
            return f.readlines()
