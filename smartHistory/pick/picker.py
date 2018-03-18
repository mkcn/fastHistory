# -*-coding:utf-8-*-

import curses

from parser import bashlex
from parser.bashParser import BashParser
from parser.manParser import ManParser
from database.dataRetriever import DataRetriever
from pick.drawer import Drawer
from pick.pageSelect import PageSelector

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = curses.KEY_UP
KEYS_DOWN = curses.KEY_DOWN
KEYS_SELECT = curses.KEY_RIGHT
KEYS_DELETE = (curses.KEY_BACKSPACE, curses.KEY_DC)
KEYS_TAB = 9
# NOTE: the KEY_ESC can be received with some delay
KEY_ESC = 27
KEYS_GO_BACK = (curses.KEY_BTAB, KEY_ESC)
KEY_RIGHT = curses.KEY_RIGHT
KEY_LEFT = curses.KEY_LEFT

DEFAULT_TITLE = "Smart History search"


class Picker(object):
    """The :class:`Picker <Picker>` object

    :param multi_select: (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
    :param indicator: (optional) custom the selection indicator
    :param default_index: (optional) set this if the default selected option is not the first one
    """

    DESCRIPTION_CONTEXT_LENGTH = 5

    DEBUG_MODE = True

    def __init__(self, search_tex="", default_index=0, multi_select=False, min_selection_count=0):

        self.search_text = search_tex
        self.search_text_lower = search_tex.lower()
        self.data_retriever = DataRetriever()
        self.options = self.data_retriever.filter(self.search_text_lower)

        self.title = DEFAULT_TITLE
        self.debug_line = "DEBUG: "
        self.indicator = "bho"
        self.all_selected = []

        self.drawer = None

        self.flags_for_info_cmd = None

        # bool to show info page
        self.is_selected_info_shown = False

        self.multi_select = multi_select
        self.min_selection_count = min_selection_count

        self.cmd_meaning = None
        self.cmd_flag1 = None

        self.index = default_index
        self.custom_handlers = {}
        self.custom_color_pairs = {}

        self.page_selector = None

        # if default_index >= len(options):
        #    raise ValueError('default_index should be less than the length of options')

        # if multi_select and min_selection_count > len(options):
        #    raise ValueError('min_selection_count is bigger than the available options, you will not be able to make any selection')

    def draw_smart(self):
        """
        main controller of page drawer
        :return:
        """
        # clear screen
        self.drawer.clear()
        # reset terminal
        self.drawer.reset()

        if self.is_selected_info_shown:
            # import this locally to improve performance when the program is loaded
            from pick.pageInfo import PageInfo
            selected_option = self.page_selector.get_selected_option()
            page_info = PageInfo(self.drawer, self.debug_line, self.page_selector)
            page_info.draw_page_info(option=selected_option,
                                     search_text_lower=self.search_text_lower,
                                     flags_for_info_cmd=self.flags_for_info_cmd)
        else:
            smart_options = self.get_smart_options()
            self.page_selector.draw_page_select(
                search_text_lower=self.search_text_lower,
                title=self.title,
                search_text=self.search_text,
                smart_options=smart_options)

        # refresh screen
        self.drawer.refresh()

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1

    def move_down(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0

    def mark_index(self):
        if self.multi_select:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)

    def get_selected(self):
        """return the current selected option as a tuple: (option, index)
           or as a list of tuples (in case multi_select==True)
        """
        if self.multi_select:
            return_tuples = []
            for selected in self.all_selected:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            return self.options[self.index], self.index

    def get_smart_options(self):
        options = []

        for index, option in enumerate(self.options):
            if index == self.index:
                options.append([True, option])
            else:
                options.append([False, option])
        return options

    def load_data_for_info_cmd(self, cmd_text):
        """
        Retrieve the info about the currently selected cmd from the man page
        :param cmd_text:    the bash cmd string
        :return:            a structured list with info for each cmd and flags
        """
        # here the man search and parse
        parser = BashParser()
        # create a result var to fill
        flags_for_info_cmd = list()
        # parse the cmd string
        cmd_parsed = bashlex.parse(cmd_text)
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
        return flags_for_info_cmd

    def run_loop(self):
        """
        Loop to capture user input keys
        """
        while True:
            # draw
            self.draw_smart()
            # wait for char
            c = self.drawer.wait_next_char()

            self.debug_line += "[" + str(c) + "]"
            if c == KEYS_UP:
                self.move_up()
            elif c == KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                if self.multi_select and len(self.all_selected) < self.min_selection_count:
                    continue
                return self.get_selected()
            elif c is KEYS_SELECT and self.multi_select:
                self.mark_index()
            elif c is -1:
                # TODO check and remove
                self.drawer.refresh()
            # tab command
            elif c is KEYS_TAB:
                self.is_selected_info_shown = True
                selected_option = self.page_selector.get_selected_option()
                self.flags_for_info_cmd = self.load_data_for_info_cmd(
                    cmd_text=selected_option[DataRetriever.INDEX_OPTION_CMD])
            elif c in KEYS_GO_BACK:
                self.is_selected_info_shown = False
            # -> command
            elif c == KEY_RIGHT:
                self.drawer.move_shift_right()
            # <- command
            elif c == KEY_LEFT:
                self.drawer.move_shift_left()
            # normal search char
            elif c in range(256):
                self.debug_line += "[chr: " + str(c) + "]"
                self.search_text += chr(c)
                self.search_text_lower += chr(c).lower()
                self.options = self.data_retriever.filter(self.search_text)
            # delete a char of the search
            elif c in KEYS_DELETE:
                if len(self.search_text) > 0:
                    self.search_text = self.search_text[:-1]
                    self.search_text_lower = self.search_text_lower[:-1]
                    self.options = self.data_retriever.filter(self.search_text_lower)
            else:
                self.debug_line += "[" + str(c) + "]"

    def _start(self, screen):
        self.drawer = Drawer(screen)
        self.page_selector = PageSelector(self.drawer, self.debug_line)
        return self.run_loop()

    def start(self):
        # TODO move curses import to drawer
        return curses.wrapper(self._start)


def pick(search_text="", default_index=0, multi_select=False, min_selection_count=0):
    """
    TODO add description
    """
    picker = Picker(search_text, default_index, multi_select, min_selection_count)
    return picker.start()


"""
    def register_custom_handler(self, key, func):
        self.custom_handlers[key] = func

    def get_title_lines(self):
        if self.title:
            return [self.title + ": " + self.search_text] + ['']
        return []


    def get_option_lines(self):
        lines = []
        for index, option in enumerate(self.options):
            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * ' '

            if self.multi_select and index in self.all_selected:
                format = curses.color_pair(1)
                line = ('{0} {1}'.format(prefix, option), format)
            else:
                line = '{0} {1}'.format(prefix, option)
            lines.append(line)

        return lines


    def get_debug_line(self):
        if self.debug_line:
            return self.debug_line.split('\n') + ['']
        return []


    def get_lines(self):
        title_lines = self.get_title_lines()
        option_lines = self.get_option_lines()
        debug_lines = self.get_debug_line()
        lines = title_lines + option_lines + debug_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line


    def draw(self):
        TODO remove this method
        draw the curses ui on the screen, handle scroll if needed

        self.screen.clear()

        x, y = 1, 1  # start point
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y  # the max rows we can draw

        lines, current_line = self.get_lines()

        # calculate how many lines we should scroll, relative to the top
        scroll_top = getattr(self, 'scroll_top', 0)
        if current_line <= scroll_top:
            scroll_top = 0
        elif current_line - scroll_top > max_rows:
            scroll_top = current_line - max_rows
        self.scroll_top = scroll_top

        lines_to_draw = lines[scroll_top:scroll_top + max_rows]

        for line in lines_to_draw:
            if type(line) is tuple:
                self.screen.addnstr(y, x, line[0], max_x - 2, line[1])
            else:
                self.screen.addnstr(y, x, line, max_x - 2)
            if y == 1:
                self.screen.addstr(" ", curses.color_pair(1))
            y += 1

        self.screen.refresh()
    """