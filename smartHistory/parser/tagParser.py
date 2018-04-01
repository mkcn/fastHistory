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

    TAGS_REGEXP = "^([0-9a-zA-Z ]*#)*([0-9a-zA-Z @])+$"

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
                                1 description string
                                2 tag array
        """

        try:
            sections = cmd.split(TagParser.TAG_SIGN, maxsplit=1)
            # at least one
            if len(sections) == 2:
                clean_cmd = sections[0]
                section_tags = sections[1]
                logging.debug("last section tag: " + section_tags)

                # TODO use regex to match tags and description
                # match = re.search(TagParser.TAGS_REGEXP, section_tags)

                # do not use group, i do not think it supports repeated groups
                # vals = m.groups()

                if TagParser.DESCRIPTION_SIGN in section_tags:
                    sections_desc = section_tags.split(TagParser.DESCRIPTION_SIGN)
                    section_description = sections_desc[1]
                    section_tags = sections_desc[0]
                else:
                    section_description = None

                tags = section_tags.split(TagParser.TAG_SIGN)
                # clean tag list from spaces
                for i in range(len(tags)):
                    tags[i] = tags[i].strip()
                    logging.debug("TAG found: '" + tags[i] + "'")
            else:
                clean_cmd = cmd
                tags = []
                section_description = None
                logging.debug("no # found")
        except:
            logging.error("error with TAG parser")
            clean_cmd = cmd
            section_description = None
            tags = []
        try:
            if section_description:
                description = section_description
            else:
                # TODO parse cmd and find cmd meaning from man page
                description = None
        except:
            description = None
            logging.error("error with CMD parser")

        return [clean_cmd, description, tags]