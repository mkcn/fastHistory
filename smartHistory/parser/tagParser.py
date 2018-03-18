import re

import logging

from parser import bashlex


class TagParser(object):
    """
    Class used to parse input commands
    """

    COMMENT = "#"
    PRIVACY_SIGN = "##"
    TAG_SEPARATOR = ","

    TAGS_REGEXP = "^([0-9a-zA-Z ]*,)*([0-9a-zA-Z ])+$"

    @staticmethod
    def is_privacy_mode_enable(cmd):
        if cmd.endswith(TagParser.PRIVACY_SIGN):
            return True
        return False

    @staticmethod
    def parse_cmd(cmd):
        try:
            sections = cmd.split(TagParser.COMMENT)
            # at least one
            if len(sections) > 1:
                section_tags = sections[len(sections) - 1]
                logging.debug("last section tag: " + section_tags)
                # to match # tag, tag1, tag2
                match = re.search(TagParser.TAGS_REGEXP, section_tags)

                # do not use group, i do not think it supports repeated groups
                # vals = m.groups()

                tags = section_tags.split(TagParser.TAG_SEPARATOR)
                # clean tag list from spaces
                for i in range(len(tags)):
                    # TODO check if we need s.strip(' \t\n\r')
                    tags[i] = tags[i].strip()
                    logging.debug("TAG found: '" + tags[i] + "'")
            else:
                tags = []
                logging.debug("no # found")
        except:
            logging.error("error with TAG parser")
            tags = []
        try:
            # NOTE: the parser class does not show the comments, so we parse it
            # parse cmd
            parts = bashlex.parse(cmd)
            # for ast in parts:
            # print type(ast)
            # print ast.dump()
        except:
            parts = None
            logging.error("error with CMD parser")

        return [cmd, parts, tags]