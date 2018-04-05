import logging
import sre_constants
import subprocess
import re

import sys


class ManParser(object):
    """
    Class used to parse man pages
    """

    # regex notes:
    # name:
    #   - the initial space size is not fixed ( "   -a" or "       -a")
    #   - the dash can be done with different char ("-" or "—")
    #   - the search must use the IGNORE CASE option
    # flags:
    #   - the flag can be at the beginning or as secondary item ("-a" or "--all, -a" or "-a\n     --all")
    #       - each item must start with "-"
    #   - after a flag we can found:
    #                       - comma     -a, --other
    #                       - equal     -a=PATTERN
    #                       - bracket   -a[=WHEN]
    # - the flag is always preceded by a new line ("\n       -a")
    _regex_name = "^NAME\n {2,7}%s {1,3}[-—] (.*\n( +.*\n)*)$"
    _regexp_flag = r"^(\n {2,7}-.+)?\n {2,7}(-.+, )*%s((\[)?[,=].+(\])?)?( .*)?\n( +.*\n)*$"
    _regex_name_no_group = "^ {7}ls - .*"

    _error_man_page_message = "<man page not found>"

    INDEX_IS_FIRST_LINE = 0
    INDEX_MEANING_VALUE = 1

    def __init__(self):
        self.cmd = None
        self.man_page = None

    def load_man_page(self, cmd):
        """
        execute "man cmd"
        More info: https://stackoverflow.com/a/4760517/6815066

        :param cmd: command string
        :return:    True if man page is found, False otherwise
        """
        self.cmd = cmd
        try:
            self.man_page = subprocess.check_output(["man", cmd]).decode('utf-8')
            return True
        except subprocess.CalledProcessError as e:
            logging.error("load_man_page: " + str(cmd))
            self.man_page = None
            return False

    def get_flag_meaning(self, flag):
        final_result = []
        if self.man_page is None:
            return None
        else:
            try:
                result = re.search(self._regexp_flag % flag, self.man_page, re.MULTILINE)
                if result is not None:
                    result = result.group(0)
                else:
                    logging.debug("get_flag_meaning: regex does not match")
                    return None
            except sre_constants.error:
                logging.error("flag meaning parser: ", sys.exc_info()[0])
                return None

        rows = result.split("\n")
        first = True
        for i in range(len(rows)):
            # remove starting and ending spaces
            row = rows[i].strip()
            if len(row) > 0:
                if first:
                    # this check if done to handle the case of flags on multi lines ( es "-a\n--all")
                    if flag in row:
                        first = False
                    final_result.append([True, row])
                else:
                    final_result.append([False, row])
        return final_result

    def get_cmd_meaning(self):
        if self.man_page is None:
            logging.error("get_cmd_meaning: man_page is empty")
            return None
        else:
            search = re.search(self._regex_name % self.cmd, self.man_page, re.MULTILINE | re.IGNORECASE)
            if search is not None:
                result = search.group(1)
            else:
                logging.debug("get_cmd_meaning: regex does not match")
                return None

        final_result = []
        rows = result.split("\n")
        first = True
        for i in range(len(rows)):
            # remove starting and ending spaces
            row = rows[i].strip()
            if len(row) > 0:
                if first:
                    first = False
                    # [INDEX_IS_FIRST_LINE, INDEX_MEANING_VALUE]
                    final_result.append([True, row])
                else:
                    # [INDEX_IS_FIRST_LINE, INDEX_MEANING_VALUE]
                    final_result.append([False, row])

        return final_result


"""
x = ManParser()
cmd = "ls"
x.get_man_page(cmd)
print ("info about: " + cmd + "\n")
print (x.get_cmd_meaning())
print ("\n")
print (x.get_flag_meaning("-l"))
print (x.get_flag_meaning("-a"))
print (x.get_flag_meaning("-A"))
"""

