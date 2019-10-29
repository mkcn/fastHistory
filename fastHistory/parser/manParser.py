import logging
import sre_constants
import subprocess
import re
import sys


class ManParser(object):
    """
    Class used to parse man pages
    """

    # regex notes
    #   - the initial space size is not fixed ( "   -a" or "       -a")
    #   - the dash can be done with different char ("-" or "—")
    #   - the command name (before the dash) can be different from the man parameters:
    #       - uppercase letters                     Wget - ......
    #       - same map page for similar commands    grep, egrep, fgrep, rgrep - ......
    # Examples:
    #       "NAME\n      ls - list directory contents" > group(0) = "list directory contents"
    #       "NAME\n   grep, egrep, fgrep - print lines matching a pattern" > group(0) = "print lines matching a pattern"
    _regex_name = "^NAME\n {2,7}" \
                  ".*" \
                  " (?:-|—|--) " \
                  "(.*\n( +.*\n)*)$"
    # regex notes
    #   - (?:OPTIONS)?    means that the previous line can be empty or with the 'OPTIONS' string
    #   - "%s" is a dynamic field of the regex and it is replaced with the flag to search
    #   - the flag can be at the beginning or as secondary item ("-a" or "--all, -a" or "-a\n     --all")
    #       - each item must start with "-"
    #   - after a flag we can found:
    #                       - comma     -a, --other
    #                       - equal     -a=PATTERN
    #                       - bracket   -a[=WHEN]
    # - the flag is always preceded by a new line ("\n       -a")
    # Examples:
    #       "OPTIONS\n       -o outputfile\n               Specify where the output is to be written.
    #       "\n      -a, --all\n        do not ignore entries starting with ."
    #       "\n      -q\n--quiet     Turn off Wget's output."

    _regexp_flag = r"^(?:OPTIONS)?((\n {2,7}-.+)?" \
                   r"\n {2,7}(-.+[,;] )*" \
                   r"%s" \
                   r"((\[)?[,;=].+(\])?)?" \
                   r"( .*)?" \
                   r"\n" \
                   r"( +.*\n)*)$"
    _regex_name_no_group = "^ {7}ls - .*"

    INDEX_IS_FIRST_LINE = 0
    INDEX_MEANING_VALUE = 1

    def __init__(self):
        self.cmd = None
        self.man_page = None

    def load_man_page(self, cmd):
        """
        execute "man cmd"
        More info: https://stackoverflow.com/a/4760517/6815066
        Note: if the command takes more than 1 second it is terminated (TimeoutExpired)
              This avoids to block the UI if the man command does not respond

        :param cmd: command string
        :return:    True if man page is found, False otherwise
        """
        self.cmd = cmd
        try:
            self.man_page = subprocess.check_output(
                ["man", cmd],
                stderr=subprocess.DEVNULL,
                timeout=1).decode('utf-8')
            # man command uses "Backspace" characters to show words bold
            # in macOS this special char is still present in the subprocess output and must be removed
            self.man_page = re.sub(r'.\x08', '', self.man_page)
            return True
        except subprocess.CalledProcessError as e:
            logging.info("load_man_page - man page not found for: " + str(cmd))
            self.man_page = None
            return False
        except subprocess.TimeoutExpired as e:
            logging.error("load man page - timeout: " + str(cmd))
            self.man_page = None
            return False
        except PermissionError as e:
            logging.error("load man page - permission denied: " + str(cmd))
            self.man_page = None
            return False

    def open_interactive_man_page(self, cmd=None):
        """
        open the real interactive man page
        :return:    return code of the man command
        """
        if cmd is not None:
            return subprocess.call(["man", cmd])
        elif self.cmd is not None:
            return subprocess.call(["man", self.cmd])
        else:
            return None

    def get_flag_meaning(self, flag):
        """
        parse the man page and find the description of the given flags (example: -a)
        example of return [('True','this is the first line'), ('False','this is the second line')]

        :param flag:
        :return:        array of tuples
        """
        final_result = []
        if self.man_page is None:
            return None
        else:
            try:
                result = re.search(self._regexp_flag % flag, self.man_page, re.MULTILINE)
                if result is not None:
                    # get group (1) and not the all string
                    result = result.group(1)
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
                    final_result.append((True, row))
                else:
                    final_result.append((False, row))
        return final_result

    def get_cmd_meaning(self):
        """
        parse the man page and find the description of the current command (example: ls)
        example of return [('True','this is the first line'), ('False','this is the second line')]

        :return:        array of tuples
        """
        if self.man_page is None:
            logging.error("get_cmd_meaning: man_page is empty")
            return None
        else:
            search = re.search(self._regex_name, self.man_page, re.MULTILINE)
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
                    final_result.append((True, row))
                else:
                    # [INDEX_IS_FIRST_LINE, INDEX_MEANING_VALUE]
                    final_result.append((False, row))

        return final_result

