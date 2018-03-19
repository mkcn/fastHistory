
import subprocess
import re


class ManParser(object):
    """
    Class used to parse man pages
    """

    _regexp_flag = r"^ {4,7}(.+, )*%s([,=].+)?( .*)?\n( +\S.*\n)*$"
    _regex_name = "^NAME\n {4,7}%s [-—] (.*)$"  # usually just 7 space
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
            self.man_page = None
            return False

    def get_flag_meaning(self, flag):
        final_result = []
        if self.man_page is None:
            return None
        else:
            result = re.search(self._regexp_flag % flag, self.man_page, re.MULTILINE)
            if result is not None:
                result = result.group(0)
            else:
                return None

        rows = result.split("\n")
        for i in range(len(rows)):
            # remove starting and ending spaces
            row = rows[i].strip()
            if len(row) > 0:
                if i == 0:
                    first = True
                else:
                    first = False
                final_result.append([first, row])

        return final_result

    def get_cmd_meaning(self):
        if self.man_page is None:
            return None
        else:
            search = re.search(self._regex_name % self.cmd, self.man_page, re.MULTILINE)
            if search is not None:
                result = search.group(1)
            else:
                return None

        final_result = []
        rows = result.split("\n")
        for i in range(len(rows)):
            # remove starting and ending spaces
            row = rows[i].strip()
            if len(row) > 0:
                if i == 0:
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

