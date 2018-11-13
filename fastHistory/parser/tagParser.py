import re
import logging


class TagParser(object):
    """
    Class used to parse input commands
    # TODO rename into "InputParser"
    """

    INDEX_CMD = 0
    INDEX_DESC = 1
    INDEX_TAGS = 2

    TAG_SIGN = "#"
    DESCRIPTION_SIGN = "@"
    PRIVACY_SIGN = "##"

    EMTPY_STRING = ""

    # https://regex101.com/r/Cs8C45/3
    # examples:
    #       ls - la  #
    #       ls - la  # 1
    #       ls - la  # 2#2
    #       ls - la  # 1#2#3 @Mün
    #       ls - la  # 1# 2#3 @Mün
    #       ls - la  # 1# 2 #3 @Mün
    #       ls - la  # 1#2	 @desc
    #       ls - la  # @desc
    #       echo \  # toignore #1
    #       echo
    #       "#toignore"  # 1-2
    #       echo
    #       "#toignore"  # @desc
    #       ls - la  # toignore
    # notes:
    #   - before each # a space is needed
    #   - before @ a space is NOT needed
    TAGS_REGEXP_INSERT_CMD = "((?:\ #[\w\d\-\_\ \t]*)+)(@[\w\d\-\_\.\,\!\?\ \t\:\;\%\+\(\)]*)?$"
    # notes:
    #   - it can start with #
    #   - it can start with @
    #   - unless the string start with them, before each # and @ a space is needed
    TAGS_REGEXP_SEARCH_CMD = "((?:(?:^#|\ #)[\w\d\-\_\ \t]*)*)((?:^@|\ @)[\w\d\-\_\.\,\!\?\ \t\:\;\%\+\(\)]*)?$"
    # general
    #   - tag: allowed special chars: ' ' '-' '_' '\t'
    #   - description: allowed special chars: '-' '_' '.' ',' '!' '?' ' ' '\t' ':' ';' '%' '+' '(' ')'
    INPUT_TAGS_REGEXP = "^\ *((?:(?:#|\ #)[\w\d\-\_\ \t]*)*)$"
    INPUT_DESCRIPTION_REGEXP = "^\ *(@[\w\d\-\_\.\,\!\?\ \t\:\;\%\+\(\)]*)$"

    @staticmethod
    def is_privacy_mode_enable(cmd):
        if cmd.endswith(TagParser.PRIVACY_SIGN):
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
        match = re.search(TagParser.INPUT_TAGS_REGEXP, tags_str, flags=re.UNICODE)
        if match:
            logging.debug("tag parser: regex matches")
            tags_str = match.group(1)
        else:
            logging.error("tag parser: regex does NOT match")
            return None

        tags = []

        if tags_str is TagParser.EMTPY_STRING:
            return []

        if tags_str is not None:
            logging.debug("tags_str: " + str(tags_str))
            tags_tmp = tags_str.split(TagParser.TAG_SIGN)
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
        if description is TagParser.EMTPY_STRING:
            return TagParser.EMTPY_STRING

        match = re.search(TagParser.INPUT_DESCRIPTION_REGEXP, description, flags=re.UNICODE)
        if match:
            logging.debug("description parser: regex matches")
            desc_str = match.group(1)
        else:
            logging.error("description parser: regex does NOT match")
            return None

        # remove @ and spaces from description
        if desc_str is not None:
            logging.debug("description parser - desc_str: " + desc_str)
            if desc_str[0] == TagParser.DESCRIPTION_SIGN:
                desc = desc_str[1:].strip()
            else:
                logging.error("description parser - description does not start with @")
                desc = None
        else:
            logging.error("description parser - description is null")
            desc = None

        return desc

    @staticmethod
    def parse_cmd(cmd, is_search_cmd=False):
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

        if is_search_cmd:
            match = re.search(TagParser.TAGS_REGEXP_SEARCH_CMD, cmd, flags=re.UNICODE)
        else:
            match = re.search(TagParser.TAGS_REGEXP_INSERT_CMD, cmd, flags=re.UNICODE)

        if match:
            logging.debug("tag parser: regex matches")
            tags_str = match.group(1)
            desc_str = match.group(2)

            char_to_cut = 0

            if tags_str:
                char_to_cut += len(tags_str)
            if desc_str:
                char_to_cut += len(desc_str)

            if char_to_cut != 0:
                cmd = cmd[:-char_to_cut]
        else:
            logging.debug("tag parser: regex does NOT match")
            return None

        # tags
        tags = []
        if tags_str is not None and tags_str is not TagParser.EMTPY_STRING:
            logging.debug("tags_str: " + str(tags_str))
            tags_tmp = tags_str.split(TagParser.TAG_SIGN)
            if len(tags_tmp) >= 2:
                tags_tmp = tags_tmp[1:]
                for i in range(len(tags_tmp)):
                    # remove spaces from each tag
                    tag = tags_tmp[i].strip()
                    #if tag != "":
                    tags.append(tag)
            else:
                tags = []
        else:
            tags = []

        # remove @ and spaces from description
        if desc_str is not None:
            logging.debug("desc_str: " + desc_str)
            if desc_str[0] == TagParser.DESCRIPTION_SIGN:
                desc = desc_str[1:].strip()
            else:  # desc_str[1] == TagParser.DESCRIPTION_SIGN:
                desc = desc_str[2:].strip()
        else:
            desc = None

        return [cmd, desc, tags]

