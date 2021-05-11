import logging
import os
import difflib
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from fastHistory.parser.InputData import InputData
    from fastHistory.tldr.tldrParserThread import TLDRParseThread


class ParsedTLDRExample(object):

    class Type:
        TITLE = 0
        CMD_DESC = 1
        CMD_DESC_MORE_INFO = 2
        EXAMPLE = 3
        EXAMPLE_DESC = 4
        OTHER = 5

    INDEX_EXAMPLE_TYPE = 0
    INDEX_EXAMPLE_VALUE = 1

    def __init__(self):
        self.command = ""
        self.cmd_folder = ""
        self.rows = []
        self.url_more_info = None

    def set_command(self, command: str) -> None:
        self.command = command

    def get_command(self) -> str:
        return self.command

    def get_rows(self) -> list:
        return self.rows

    def get_current_selected_example(self, row_index: int) -> Optional[str]:
        if row_index < len(self.rows):
            return self.rows[row_index][self.INDEX_EXAMPLE_VALUE]
        else:
            return None

    def append_example_row(self, row: str) -> None:
        self.rows.append([self.Type.EXAMPLE, row])

    def append_generic_row(self, row: str) -> None:
        self.rows.append([self.Type.OTHER, row])

    def append_example_desc_row(self, row: str) -> None:
        self.rows.append([self.Type.EXAMPLE_DESC, row])

    def append_cmd_desc_row(self, row: str) -> None:
        self.rows.append([self.Type.CMD_DESC, row])

    def append_cmd_desc_more_info_row(self, row: str) -> None:
        self.rows.append([self.Type.CMD_DESC_MORE_INFO, row])

    def get_delta_next_example_index(self, examples_index: int) -> int:
        delta_next_example_index = 0
        for i in range(len(self.rows)):
            if i > examples_index:
                delta_next_example_index += 1
                if self.rows[i][0] == self.Type.EXAMPLE:
                    return delta_next_example_index
        return 0

    def get_delta_previous_example_index(self, examples_index: int) -> int:
        delta_previous_example_index = 0
        rows_count = len(self.rows)
        for i in range(rows_count):
            i_rev = rows_count - i
            if i_rev < examples_index:
                delta_previous_example_index += 1
                if self.rows[i_rev][0] == self.Type.EXAMPLE:
                    return delta_previous_example_index
        return 0

    def get_first_example_index(self) -> int:
        first_example_index = 0
        for i in range(len(self.rows)):
            if self.rows[i][0] == self.Type.EXAMPLE:
                first_example_index = i
                return first_example_index
        return 0

    def set_url_more_info(self, url_more_info):
        self.url_more_info = url_more_info

    def get_url_more_info(self):
        return self.url_more_info

    def has_url_more_info(self):
        return self.url_more_info is not None


class TLDRParser(object):
    """
    Offline search of command from TLDR pages (source: https://github.com/tldr-pages/tldr)
    """

    FOLDER_TLDR_PAGES = "tldr/pages/"
    PAGE_CMD_TITLE_CHAR = "#"
    PAGE_CMD_DESC_CHAR = ">"
    PAGE_CMD_DESC_MORE_INFO_STR = "> More information"
    PAGE_EXAMPLE_CHAR = "`"
    PAGE_EXAMPLE_DESC_CHAR = "-"

    INDEX_TLDR_MATCH_CMD_FOLDER = 1
    INDEX_TLDR_MATCH_CMD = 2
    INDEX_TLDR_MATCH_FULL_PATH = 3
    INDEX_TLDR_MATCH_AVAILABILITY = 4

    def __init__(self, cached_in_memory_pages=None, enabled_os_folders=None):
        # TODO read from configuration or make dynamic based on OS ( enabled_os_folders: "linux", "windows", "osx"
        if enabled_os_folders is not None:
            self.enabled_os_folders = ["common"] + enabled_os_folders
        else:
            self.enabled_os_folders = ["common", "linux"]  # "windows", "osx",
        self.pages_path = os.path.abspath(os.path.dirname(__file__)) + "/" + self.FOLDER_TLDR_PAGES
        if not os.path.isdir(self.pages_path):
            logging.error("TLDR pages path not found: %s" % self.pages_path)
        if cached_in_memory_pages is None:
            self.cached_in_memory_pages = {}
        else:
            self.cached_in_memory_pages = cached_in_memory_pages

    def _read_file(self, file_full_path: str) -> list:
        context = []
        with open(file_full_path, "r") as f:
            for line in f:
                context.append(line)
        return context

    def find_match_command(self, input_data: "InputData", thread: "TLDRParseThread" = None) -> Optional[list]:
        # NO empty, already trimmed
        words = input_data.get_all_words()
        words = [word.lower() for word in words]
        result = []
        words_dict = {}
        try:
            for os_folder in self.enabled_os_folders:
                for root, dirs, fnames in os.walk(self.pages_path + os_folder):
                    for fname in fnames:
                        # this remove any empty word
                        words_dict = dict((word, 0) for word in words if len(word) > 0)
                        total_weight = 0

                        file_full_path = os.path.join(root, fname)
                        page = self.cached_in_memory_pages.get(os_folder + "/" + fname)
                        if page is None:
                            self.cached_in_memory_pages[os_folder + "/" + fname] = self._read_file(file_full_path)
                        # if dict is not empty read the file
                        if words_dict:
                            if thread and thread.has_been_stopped():
                                logging.debug("find_match_command: thread stopped, stop the research")
                                return []
                            # TODO try to use mmapls
                            # map_file = mmap.mmap(f.fileno(), 0, prot=mmap.ACCESS_READ)
                            for line in self.cached_in_memory_pages[os_folder + "/" + fname]:
                                number_of_matches_in_a_line = 0
                                for word in words_dict.keys():
                                    if word in line.lower():
                                        number_of_matches_in_a_line += 1
                                        first_char = line[0]
                                        if first_char == self.PAGE_CMD_TITLE_CHAR:
                                            # check if title matches (e.g. "# tar\n")
                                            command = line[2:-1].strip().lower()
                                            ratio_match = difflib.SequenceMatcher(None, word, command).ratio()
                                            weight = 20 * ratio_match
                                        elif first_char == self.PAGE_CMD_DESC_CHAR:
                                            if line.startswith(self.PAGE_CMD_DESC_MORE_INFO_STR):
                                                weight = 1
                                            else:
                                                weight = 3
                                        elif first_char == self.PAGE_EXAMPLE_DESC_CHAR:
                                            weight = 2
                                        elif first_char == self.PAGE_EXAMPLE_CHAR:
                                            weight = 1
                                        else:
                                            # ignore line without the correct format
                                            weight = 0
                                        words_dict[word] += 1
                                        total_weight += (weight * number_of_matches_in_a_line)
                        if all(count > 0 for count in words_dict.values()):
                            if fname.endswith(".md"):
                                cmd_name = fname[:-3]
                            else:
                                logging.error("find_match_command: fname does not ends with md: %s" % fname)
                                cmd_name = fname
                            # NOTE: the system availability of the command (5' value) is calculated later only if needed
                            result.append([total_weight, os_folder, cmd_name, file_full_path, None])
            if words_dict:
                result.sort(key=TLDRParser._find_match_command_sort_key, reverse=True)
            return result
        except Exception as e:
            logging.error("find_match_command: %s" % e)
            return result

    @staticmethod
    def _find_match_command_sort_key(arr):
        return arr[0]

    @staticmethod
    def _get_url_from_more_info_row(row):
        if "<" in row:
            row = row.split("<")[1]
            if ">" in row:
                return row.split(">")[0]
            else:
                logging.error("row with wrong url format: %s" % row)
        else:
            logging.error("row with wrong url format: %s" % row)
            return row

    def get_tldr_cmd_examples(self, tldr_page_match: list) -> ParsedTLDRExample:
        parsed_tldr_example = ParsedTLDRExample()
        path_tldr_page = tldr_page_match[self.INDEX_TLDR_MATCH_FULL_PATH]
        with open(path_tldr_page) as f:
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    parsed_tldr_example.append_generic_row(line)
                else:
                    first_char = line[0]
                    if first_char == self.PAGE_CMD_TITLE_CHAR:
                        parsed_tldr_example.set_command(line)
                    elif first_char == self.PAGE_EXAMPLE_CHAR:
                        last_char = line[-1]
                        if last_char == self.PAGE_EXAMPLE_CHAR and len(line) > 2:
                            clean_cmd = line[1:-1]
                            parsed_tldr_example.append_example_row(clean_cmd)
                        else:
                            parsed_tldr_example.append_example_row(line)
                            logging.error("bad format: %s -> %s" % (path_tldr_page, line))
                    elif line.startswith(self.PAGE_CMD_DESC_MORE_INFO_STR):
                        parsed_tldr_example.set_url_more_info(TLDRParser._get_url_from_more_info_row(line))
                        parsed_tldr_example.append_generic_row(line)
                    else:
                        parsed_tldr_example.append_generic_row(line)
        return parsed_tldr_example

    @staticmethod
    def remove_brackets_from_str(line_to_clean):
        if '[' in line_to_clean and ']' in line_to_clean:
            obi = line_to_clean.index('[')
            cbi = line_to_clean.index(']')
            if obi == cbi - 2:
                line_to_clean = line_to_clean[:obi] + line_to_clean[obi + 1] + line_to_clean[obi + 2 + 1:]
                return TLDRParser.remove_brackets_from_str(line_to_clean)
            else:
                return line_to_clean
        else:
            return line_to_clean

    def format_tldr_pages(self):
        """
        this is used only by the update_tldr_pages.sh script
        :return:
        """
        try:
            count = 0
            for root, dirs, fnames in os.walk(self.pages_path):
                for fname in fnames:
                    read_lines = []
                    modified = False
                    if not fname.endswith(".md"):
                        continue
                    fnamein = os.path.join(root, fname)
                    fnameout = os.path.join(root, fname) + ".tmp"
                    fin = open(fnamein, "r")
                    fout = open(fnameout, "w")
                    last_line_first_char = ""
                    for line in fin:
                        line = line.strip()
                        if len(line) > 0:
                            # check if contain "[a]" flag syntax and replace it
                            first_char = line[0]
                            if first_char is self.PAGE_EXAMPLE_DESC_CHAR:
                                line = self.remove_brackets_from_str(line)
                                # step 3: remove ':' char from end of line
                                last_char = line[-1]
                                if last_char == ":":
                                    line = line[:-1]
                            last_line_first_char = first_char
                        else:
                            # remove empty line between examples and relative description lines
                            # and between title and description
                            if last_line_first_char == self.PAGE_EXAMPLE_DESC_CHAR \
                                    or last_line_first_char == self.PAGE_CMD_TITLE_CHAR \
                                    or last_line_first_char == "":
                                continue
                            last_line_first_char = ""
                        read_lines.append(line + '\n')

                    fin.close()
                    fout.writelines(read_lines)
                    fout.truncate()
                    fout.close()

                    os.remove(fnamein)
                    os.rename(fnameout, fnamein)

                    count += 1
            return "%d pages have been correctly formatted" % count
        except Exception as e:
            return "Error: %s" % e



