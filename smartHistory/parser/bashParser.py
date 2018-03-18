import logging


class BashParser(object):
    """
    Class to parse bash commands and handle flags
    """

    logFile = "/home/mart/Desktop/file.log"

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
        self.logger = logging.getLogger(self.logFile)
        self.logger.setLevel(logging.INFO)

    def get_flags_from_bash_node(self, bash_node, result, cmd_main=None, first_cmd=False):
        self.logger.debug("result: " + str(result))
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
                    self.logger.debug("ignore word: " + bash_node.parts[0].word)
                    bash_node.parts = bash_node.parts[1:]

                for i in range(len(bash_node.parts)):
                    if i == 0:
                        cmd_main = self.get_flags_from_bash_node(bash_node.parts[i], result, first_cmd=True)
                    else:
                        self.get_flags_from_bash_node(bash_node.parts[i], result, cmd_main=cmd_main, first_cmd=False)
            # check if node is a word
            elif bash_node.kind == self.CMD_NODE_TYPE_WORD:
                self.logger.info("bash_node.word word: " + bash_node.word)
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
                        self.logger.error("error cmd main null")

                self.logger.debug("word value: " + bash_node.word)
            elif getattr(bash_node, "parts", None):
                # check if node has parts
                for i in bash_node.parts:
                    self.get_flags_from_bash_node(i, result)
            else:
                self.logger.debug("Other kind: " + bash_node.kind + "\n")

        else:
            self.logger.debug("Unknown obj: " + str(bash_node) + "\n")

    def get_flags(self, bash_node, result, cmd_main=None, first_cmd=False):

        if type(bash_node) == list:
            for i in bash_node:
                self.get_flags(i, result)
        else:
            self.logger.debug("kind: " + bash_node.kind)
            if bash_node.kind == self.CMD_NODE_TYPE_LIST:
                for i in bash_node.parts:
                    self.get_flags(i, result)
            elif bash_node.kind == self.CMD_NODE_TYPE_COMPOUND:
                for i in bash_node.list:
                    self.get_flags(i, result)
            elif bash_node.kind == self.CMD_NODE_TYPE_PIPELINE:
                self.logger.debug("PIPELINE: " + str(bash_node))
                for i in bash_node.parts:
                    self.get_flags(i, result)
            elif bash_node.kind == self.CMD_NODE_TYPE_CMD:
                items_len = len(bash_node.parts)
                if items_len > 0 and bash_node.parts[0].kind == self.CMD_NODE_TYPE_WORD and bash_node.parts[0].word in self.WORD_TO_IGNORE:
                    self.logger.debug("ignore word: " + bash_node.parts[0].word)
                    bash_node.parts = bash_node.parts[1:]

                for i in range(len(bash_node.parts)):
                    if i == 0:
                        cmd_main = self.get_flags(bash_node.parts[i], result, first_cmd=True)
                    else:
                        self.get_flags(bash_node.parts[i], result, cmd_main=cmd_main, first_cmd=False)
            elif bash_node.kind == self.CMD_NODE_TYPE_WORD:
                if first_cmd:
                    found = False
                    for item in result:
                        if item[0] == bash_node.word:
                            found = True
                            break
                    if not found:
                        result.append([bash_node.word, []])
                    return bash_node.word
                else:
                    if cmd_main is not None:
                            for item in result:
                                if item[0] == cmd_main:
                                    found = False
                                    for flag in item[1]:
                                        if flag == bash_node.word:
                                            found = True
                                            break
                                    if not found:
                                        item[1].append(bash_node.word)
                                    break
                    else:
                        self.logger.error("error cmd main null")

                self.logger.debug("word value: " + bash_node.word)
            elif bash_node.kind in self.CMD_NODE_TYPE_OPERATOR:
                self.logger.debug("OP: " + str(bash_node.op))
            elif bash_node.kind in self.CMD_NODE_TYPE_PIPE:
                self.logger.debug("PIPE: " + str(bash_node.pipe))
            else:
                print("BHO: " + bash_node.kind + "\n")
                self.logger.debug("BHO: " + bash_node.kind + "\n")

    @staticmethod
    def decompose_possible_concatenated_flags(flag_string):
        """
        Given a possible concatenated flag string it return an array with all the flags decomposed
        :param flag_string:     example: -lsv
        :return:                example: ['-l','-s','-v']
        """
        flags = []
        flag_dash = '-'
        if flag_string.startswith(flag_dash):
            flag_string = flag_string[1:]
            flag_len = len(flag_string)
            if flag_len == 1:
                # basic flag (example: -l)
                flags.append(flag_dash + flag_string)
            elif flag_len > 1:
                # combined flags (example: -lsv)
                for c in flag_string:
                    flags.append(flag_dash + c)
            else:
                # '-' case
                pass
        else:
            # only flags which start with '-' are currently supported
            # possible improvement: support generic flags (such as "git add ..")
            pass
        return flags

