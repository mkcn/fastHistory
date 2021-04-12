import logging
import os


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
        self.rows = []

    def set_command(self, command: str) -> None:
        self.command = command

    def get_command(self) -> str:
        return self.command

    def get_rows(self) -> list:
        return self.rows

    def get_current_selected_example(self, row_index: int) -> str:
        if row_index < len(self.rows):
            return self.rows[row_index][self.INDEX_EXAMPLE_VALUE]
        else:
            logging.error("get_current_selected_example, row_index out of bound: (%s, %s)" % (row_index, len(self.rows)))
            return ""

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
                    break
        return delta_next_example_index

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

    INDEX_TLDR_MATCH_FULL_PATH = 2

    def __init__(self, enabled_os_folders=None):
        # TODO read from configuration or make dynamic based on OS ( enabled_os_folders: "linux", "windows", "osx"
        if enabled_os_folders is not None:
            self.enabled_os_folders = ["common"] + enabled_os_folders
        else:
            self.enabled_os_folders = ["common", "linux"]  # "windows", "osx",
        self.pages_path = os.path.abspath(os.path.dirname(__file__)) + "/" + self.FOLDER_TLDR_PAGES
        if not os.path.isdir(self.pages_path):
            logging.error("TLDRParser: %s not found " % self.pages_path)

    def find_match_command(self, words):
        # NO empty, already trimmed
        words = [word.lower() for word in words]
        result = []
        for os_folder in self.enabled_os_folders:
            for root, dirs, fnames in os.walk(self.pages_path + os_folder):
                for fname in fnames:
                    # this remove any empty word
                    words_dict = dict((word, 0) for word in words if len(word) > 0)
                    total_weight = 0
                    file_full_path = os.path.join(root, fname)
                    # if dict is not empty read the file
                    if words_dict:
                        with open(file_full_path) as f:
                            for line in f:
                                for word in words_dict.keys():
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
                        logging.debug("find_match_command: %s -> %s" % (file_full_path, words_dict))
                        cmd_to_draw = os_folder + "/" + cmd_name
                        result.append([total_weight, cmd_to_draw, file_full_path])

        result.sort(key=TLDRParser._find_match_command_sort_key, reverse=True)
        return result

    @staticmethod
    def _find_match_command_sort_key(arr):
        return arr[0]

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
                            logging.error("parse_tld_page - bad format: %s -> %s" % (path_tldr_page, line))
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




