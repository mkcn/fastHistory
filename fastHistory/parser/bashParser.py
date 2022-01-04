import logging
import threading

from fastHistory.parser.manParser import ManParser


class BashParser(object):
    """
    Class to parse bash commands and handle flags
    """

    CMD_NODE_TYPE_CMD = "command"
    CMD_NODE_TYPE_WORD = "word"
    CMD_NODE_TYPE_LIST = "list"
    CMD_NODE_TYPE_OPERATOR = "operator"
    CMD_NODE_TYPE_PIPELINE = "pipeline"
    CMD_NODE_TYPE_PIPE = "pipe"
    CMD_NODE_TYPE_COMPOUND = "compound"

    INDEX_VALUE = 0
    INDEX_MEANING = 1

    INDEX_CMD = 0
    INDEX_FLAGS = 1

    WORD_TO_IGNORE = ["sudo", "true", "false"]

    def __init__(self):
        pass

    def get_flags_from_bash_node(self, bash_node, result, cmd_main=None, first_cmd=False):
        logging.debug("result: %s" % str(result))
        # check if node is a list
        if type(bash_node) == list:
            for i in bash_node:
                self.get_flags_from_bash_node(i, result)
        elif hasattr(bash_node, "list"):
            for i in bash_node.list:
                self.get_flags_from_bash_node(i, result)
        elif hasattr(bash_node, "kind"):
            # check if node is a command
            if bash_node.kind == self.CMD_NODE_TYPE_CMD:
                items_len = len(bash_node.parts)
                if items_len > 0 and bash_node.parts[0].kind == self.CMD_NODE_TYPE_WORD and bash_node.parts[0].word in self.WORD_TO_IGNORE:
                    logging.debug("ignore word: %s" % bash_node.parts[0].word)
                    bash_node.parts = bash_node.parts[1:]

                for i in range(len(bash_node.parts)):
                    if i == 0:
                        cmd_main = self.get_flags_from_bash_node(bash_node.parts[i], result, first_cmd=True)
                    else:
                        self.get_flags_from_bash_node(bash_node.parts[i], result, cmd_main=cmd_main, first_cmd=False)
            # check if node is a word
            elif bash_node.kind == self.CMD_NODE_TYPE_WORD:
                logging.debug("bash_node.word word: %s" % bash_node.word)
                if first_cmd:
                    found = False
                    for item in result:
                        if item[self.INDEX_CMD][self.INDEX_VALUE] == bash_node.word:
                            found = True
                            break
                    if not found:
                        result.append([[bash_node.word, None], []])
                    return bash_node.word
                else:
                    if cmd_main is not None:
                        for item in result:
                            if item[self.INDEX_CMD][self.INDEX_VALUE] == cmd_main:
                                found = False
                                for flag in item[self.INDEX_FLAGS]:
                                    if flag[self.INDEX_VALUE] == bash_node.word:
                                        found = True
                                        break
                                if not found:
                                    item[self.INDEX_FLAGS].append([bash_node.word, None])
                                break
                    else:
                        logging.error("error cmd main null")

                logging.debug("word value: %s" % bash_node.word)
            elif getattr(bash_node, "parts", None):
                # check if node has parts
                for i in bash_node.parts:
                    self.get_flags_from_bash_node(i, result)
            else:
                logging.debug("other kind: %s" % bash_node.kind)
        else:
            logging.debug("unknown obj: %s" % str(bash_node))

    @staticmethod
    def decompose_possible_concatenated_flags(flag_string):
        """
        Given a possible concatenated flag string it return an array with all the flags decomposed
        NOTE: flags like "--help" must not be decomposed

        :param flag_string:     example: -lsv
        :return:                example: ['-l','-s','-v']
        """
        flags = []
        flag_dash = '-'
        # "-" ok , "--" not
        if len(flag_string) >= 2 and flag_string[0] == flag_dash and flag_string[1] != flag_dash:
            flag_string = flag_string[1:]
            flag_len = len(flag_string)
            if flag_len == 1:
                # basic flag (example: -l)
                flags.append(flag_dash + flag_string)
            elif flag_len > 1:
                # combined flags (example: -lsv)
                for c in flag_string:
                    if str(flag_dash + c) not in flags:
                        flags.append(flag_dash + c)
            else:
                # '-' case
                pass
        else:
            # only flags which start with '-' are currently supported
            # possible improvement: support generic flags (such as "git add ..")
            pass
        return flags

    @staticmethod
    def load_data_for_info_from_man_page(cmd_text):
        """
        retrieve info about the currently selected cmd from the man page

        :param cmd_text:    the bash cmd string
        :return:            [True, structured list with info for each cmd and flags]
                            [False, error string]
        """
        # here the man search and parse
        parser = BashParser()
        # create a result var to fill
        flags_for_info_cmd = list()
        # parse the cmd string
        try:
            # the system may not have bashlex installed
            from bashlex import parse
            cmd_parsed = parse(cmd_text)
        except ImportError:
            return [False, "install bashlex to enable this"]
        except:
            return [False, "bashlex cannot read this command"]
        # find all flags for each commands
        parser.get_flags_from_bash_node(cmd_parsed, flags_for_info_cmd)
        # for each cmd and flag find the meaning from the man page
        man_parsed = ManParser()
        for item in flags_for_info_cmd:
            cmd_main = item[BashParser.INDEX_CMD]
            cmd_flags = item[BashParser.INDEX_FLAGS]
            if man_parsed.load_man_page(cmd_main[BashParser.INDEX_VALUE]):
                # save cmd meaning
                cmd_main[BashParser.INDEX_MEANING] = man_parsed.get_cmd_meaning()
                # cmd meaning found in the man page
                if cmd_main[BashParser.INDEX_MEANING]:
                    cmd_flags_updated = list()
                    for flag_i in range(len(cmd_flags)):
                        flag = cmd_flags[flag_i]
                        flag[BashParser.INDEX_MEANING] = man_parsed.get_flag_meaning(flag[BashParser.INDEX_VALUE])
                        # if flag found in the man page
                        if flag[BashParser.INDEX_MEANING]:
                            cmd_flags_updated.append(flag)
                        else:
                            # try to check if flag is concatenated
                            conc_flags = BashParser.decompose_possible_concatenated_flags(flag[BashParser.INDEX_VALUE])
                            for conc_flag in conc_flags:
                                conc_flag_meaning = man_parsed.get_flag_meaning(conc_flag)
                                cmd_flags_updated.append([conc_flag, conc_flag_meaning])
                    # set the updated flags as new list of flags, the old list is deleted
                    item[BashParser.INDEX_FLAGS] = cmd_flags_updated
        return [True, flags_for_info_cmd]


class BashParserThread(threading.Thread):

    def __init__(self, cmd_text):
        threading.Thread.__init__(self)
        self.cmd_text = cmd_text
        self.result = [False, "Loading.."]

    def run(self):
        self.result = BashParser.load_data_for_info_from_man_page(self.cmd_text)

    def get_result(self):
        return self.result
