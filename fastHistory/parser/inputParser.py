import re
import logging

from fastHistory.database.InputData import Input


class InputParser(object):
    """
    Class used to parse input commands
    """

    TAG_SIGN = "#"
    DESCRIPTION_SIGN = "@"
    PRIVACY_SIGN = "##"
    SPACE = " "

    EMTPY_STRING = ""

    # allowed chars
    TAGS_ALLOWED_CHARS = "\w\d\-\_\ \t"
    DESCRIPTION_ALLOWED_CHARS = "\w\d\-\_\.\,\!\?\ \t\:\;\%\+\(\)\\\/\'\"\`\%\$\="

    # https://regex101.com/r/ZYtE0R/2
    # notes:
    #   - before each # a space is needed
    #   - before @ a space is NOT needed
    REGEXP_INSERT_CMD = "((?:\ #[" + TAGS_ALLOWED_CHARS + "]*)+)(@[" + DESCRIPTION_ALLOWED_CHARS + "]*)?$"
    # notes:
    #   - it can start with #
    #   - it can start with @
    #   - unless the string start with them, before each # and @ a space is needed
    REGEXP_SEARCH_CMD = "((?:(?:^#|\ #)[" + TAGS_ALLOWED_CHARS + "]*)*)((?:^@|\ @)[" + DESCRIPTION_ALLOWED_CHARS + "]*)?$"
    # general
    REGEXP_INPUT_TAGS = "^\ *((?:(?:#|\ #)[" + TAGS_ALLOWED_CHARS + "]*)*)$"
    REGEXP_INPUT_DESCRIPTION = "^\ *(@[" + DESCRIPTION_ALLOWED_CHARS + "]*)$"

    @staticmethod
    def is_privacy_mode_enable(cmd):
        if cmd.endswith(InputParser.PRIVACY_SIGN):
            return True
        return False

    @staticmethod
    def parse_tags_str(tags_str):
        """
        given a (user input) tags string (from 'edit tag' page) it will parse it and it will return a set of tags
        this function use a regex as input validation

        :param tags_str:    tags string (e.g. "#tag1 #tag2    #tag3 # tag4-0 ")
        :return:            if the input is valid -> array of tags (e.g. ['tag1','tag2','tag3','tag4-0')
                            otherwise None
        """
        match = re.search(InputParser.REGEXP_INPUT_TAGS, tags_str, flags=re.UNICODE)
        if match:
            logging.debug("tag parser: regex matches")
            tags_str = match.group(1)
        else:
            logging.error("tag parser: regex does NOT match")
            return None

        tags = []

        if tags_str == InputParser.EMTPY_STRING:
            return []

        if tags_str is not None:
            logging.debug("tags_str: " + str(tags_str))
            tags_tmp = tags_str.split(InputParser.TAG_SIGN)
            if len(tags_tmp) >= 2:
                tags_tmp = tags_tmp[1:]
                for i in range(len(tags_tmp)):
                    # remove spaces from each tag
                    tag = tags_tmp[i].strip()
                    # if tag != "":
                    tags.append(tag)
                return tags
            else:
                # return empty array
                return []
        else:
            return None

    @staticmethod
    def parse_description(description):
        """
        given a (user input) description string (from 'edit description' page) it will parse it and it will return the
        description text
        this function use a regex as input validation

        :param description:    description string (e.g. "@description for a command ")
        :return:            if the input is valid -> the description text (e.g. "description for a command")
                            otherwise None
        """
        if description == InputParser.EMTPY_STRING:
            return InputParser.EMTPY_STRING

        match = re.search(InputParser.REGEXP_INPUT_DESCRIPTION, description, flags=re.UNICODE)
        if match:
            logging.debug("description parser: regex matches")
            desc_str = match.group(1)
        else:
            logging.error("description parser: regex does NOT match")
            return None

        # remove @ and spaces from description
        if desc_str is not None:
            logging.debug("description parser - desc_str: " + desc_str)
            if desc_str[0] == InputParser.DESCRIPTION_SIGN:
                desc = desc_str[1:].strip()
            else:
                logging.error("description parser - description does not start with @")
                desc = None
        else:
            logging.error("description parser - description is null")
            desc = None

        return desc

    @staticmethod
    def is_cmd_str_valid(cmd_str):
        """
        parse cmd string with the 'insert cmd' regex to check if the end matches the tags or description structure
        if yes, it is not a valid command because the command should not contains tags or descriptions
        if not, then the string is valid
        :param cmd_str: command string to evaluate
        :return:        true if valid, false otherwise
        """
        match = re.search(InputParser.REGEXP_INSERT_CMD, cmd_str, flags=re.UNICODE)

        if match:
            logging.debug("command parser: regex matches")
            tags_str = match.group(1)
            desc_str = match.group(2)

            if tags_str is None and desc_str is None:
                return True
            else:
                logging.debug("command contains tag and/or description")
                return False
        else:
            logging.debug("command parser: regex does not match (correct)")
            return True

    @staticmethod
    def adjust_multi_line_input(input):
        """
        return [True, new value] if input is multi-line
        """
        one_line_input = input
        for char in ['\\\n', '\n', '\r']:
            one_line_input = one_line_input.replace(char, '')
        if one_line_input == input:
            return [False, one_line_input]
        else:
            return [True, one_line_input]

    @staticmethod
    def parse_input(cmd, is_search_cmd=False):
        """
        parse the input cmd and retrieve the cmd, tags and description
        accepted input:     cmd_string [#[tag[#tag...]][@description]]

        examples:
                            ls -la #list#file @show list files
                            ls -la #list #file @show list files
                            ls -la #list
                            ls -la #@show list files

        :param is_search_cmd:  if true it is used the regex for search cmd, otherwise the regex for insert cmd
        :param cmd:         input console cmd
        :return:            array with following structure
                                0 cmd string without tag and description
                                1 description string
                                2 tags array
                            None in case a command without tags or description
                            None in case of generic errors
        """
        is_advanced_search = False

        if is_search_cmd:
            match = re.search(InputParser.REGEXP_SEARCH_CMD, cmd, flags=re.UNICODE)
        else:
            match = re.search(InputParser.REGEXP_INSERT_CMD, cmd, flags=re.UNICODE)

        if match:
            logging.debug("input parser: regex matches")
            tags_str = match.group(1)
            desc_str = match.group(2)

            char_to_cut = 0

            if tags_str:
                char_to_cut += len(tags_str)
            if desc_str:
                char_to_cut += len(desc_str)

            if char_to_cut != 0:
                cmd = cmd[:-char_to_cut]
            cmd = cmd.strip()
        else:
            logging.debug("input parser: regex does NOT match")
            return None

        # tags
        tags = []
        if tags_str is not None and tags_str != InputParser.EMTPY_STRING:
            logging.debug("tags_str: " + str(tags_str))
            tags_tmp = tags_str.split(InputParser.TAG_SIGN)
            if len(tags_tmp) >= 2:
                tags_tmp = tags_tmp[1:]
                for i in range(len(tags_tmp)):
                    # remove spaces from each tag
                    tag = tags_tmp[i].strip()
                    tags.append(tag)
                is_advanced_search = True
            else:
                tags = []
        else:
            tags = []

        # remove @ and spaces from description
        if desc_str is not None:
            logging.debug("desc_str: " + desc_str)
            if desc_str[0] == InputParser.DESCRIPTION_SIGN:
                desc = desc_str[1:].strip()
            else:  # desc_str[1] == InputParser.DESCRIPTION_SIGN:
                desc = desc_str[2:].strip()
            is_advanced_search = True
        else:
            desc = None

        if is_advanced_search:
            return Input(True,
                         command_str=cmd,
                         command_words=InputParser.get_list_words(cmd),
                         description=desc,
                         description_words=InputParser.get_list_words(desc),
                         tags=tags)
        else:
            return Input(False,
                         command_str=cmd,
                         command_words=InputParser.get_list_words(cmd))

    @staticmethod
    def get_list_words(string):
        if string is None:
            return []
        elif string == "":
            return ['']
        else:
            # split string
            arr_words = string.split(InputParser.SPACE)
            # removed empty strings
            return [x for x in arr_words if x]
