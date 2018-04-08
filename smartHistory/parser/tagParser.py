import re

import logging

from parser import bashlex


class TagParser(object):
    """
    Class used to parse input commands
    """

    TAG_SIGN = "#"
    DESCRIPTION_SIGN = "@"
    PRIVACY_SIGN = "##"

    # https://regex101.com/r/Cs8C45/3
    TAGS_REGEXP = "\ ((?:#[\w\d\-\_\ \t]*)+)(@[\w\d\-\_\.\,\!\?\ \t]*)?$"

    @staticmethod
    def is_privacy_mode_enable(cmd):
        if cmd.endswith(TagParser.PRIVACY_SIGN):
            return True
        return False

    @staticmethod
    def parse_cmd(cmd):
        """
        parse the input cmd and retrieve the cmd, tags and description
        accepted input:     cmd_string [#[tag[#tag...]][@description]]

        examples:
                            ls -la #list#file @show list files
                            ls -la #list #file @show list files
                            ls -la #list
                            ls -la #@show list files

        :param cmd:         input console cmd
        :return:            array with following structure
                                0 cmd string without tag and description
                                1 tags array
                                2 description string
                            None in case a command without tags or description
                            None in case of generic errors
        """

        match = re.search(TagParser.TAGS_REGEXP, cmd, flags=re.UNICODE)
        if match:
            logging.debug("tag parser: regex matches")
            tags_str = match.group(1)
            desc_str = match.group(2)
            char_to_cut = 1
            if tags_str:
                char_to_cut += len(tags_str)
            if desc_str:
                char_to_cut += len(desc_str)
            cmd = cmd[:-char_to_cut]
        else:
            logging.debug("tag parser: regex does NOT match")
            return None

        # tags
        tags = []
        tags_tmp = tags_str.split(TagParser.TAG_SIGN)
        if len(tags_tmp) >= 2:
            tags_tmp = tags_tmp[1:]
            for i in range(len(tags_tmp)):
                # remove spaces from each tag
                tag = tags_tmp[i].strip()
                if tag != "":
                    tags.append(tag)
        else:
            tags = []

        # remove @ and spaces from description
        if desc_str is not None:
            desc = desc_str[1:].strip()
        else:
            desc = None

        return [cmd, tags, desc]

