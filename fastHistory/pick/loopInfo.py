import logging

from fastHistory import DataManager
from fastHistory.parser.bashParser import BashParserThread
from fastHistory.pick.keys import Keys
from fastHistory.pick.loopEdit import LoopEdit


class LoopInfo(object):

    def __init__(self, current_selected_option, drawer, data_manager, search_t, last_column_size, context_shift, multi_select=False):

        self.drawer = drawer
        self.data_manager = data_manager
        self.search_t = search_t
        self.is_multi_select = multi_select
        self.last_column_size = last_column_size
        self.context_shift = context_shift
        self.current_selected_option = current_selected_option

    def run_loop_info(self):
        """
        Loop to capture user input keys to interact with the info page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from fastHistory.pick.pageInfo import PageInfo

        bash_parser_thread = BashParserThread(cmd_text=self.current_selected_option[DataManager.OPTION.INDEX_CMD])
        bash_parser_thread.start()
        page_info = PageInfo(self.drawer,
                             option=self.current_selected_option,
                             search_filters=self.data_manager.get_search_filters(),
                             context_shift=self.context_shift)
        loop_edit = LoopEdit(current_selected_option=self.current_selected_option,
                             drawer=self.drawer,
                             data_manager=self.data_manager,
                             context_shift=self.context_shift)

        while True:
            if page_info.has_minimum_size():
                page_info.clean_page()
                page_info.draw_page(data_from_man_page=bash_parser_thread.get_result())
                page_info.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char(multi_threading_mode=bash_parser_thread.is_alive())
            logging.debug("pressed key: %s" % repr(c))

            if c == Keys.KEY_TIMEOUT:
                continue
            elif c in Keys.KEYS_ENTER:
                return [True, "select"]
            elif c == Keys.KEY_CTRL_SPACE:
                return [True, "copy"]
            # delete current selected option
            elif c == Keys.KEY_CANC:
                self.data_manager.delete_element(self.current_selected_option[DataManager.OPTION.INDEX_CMD])
                return [False, "deleted"]
            # go back to select page
            elif c == Keys.KEY_TAB or c == Keys.KEY_SHIFT_TAB or c == Keys.KEY_ESC:
                return [False, None]
            # open man page
            # elif c == 109:  # char 'm'
                # TODO fix and show description in help line
                # from fastHistory.console import consoleUtils
                # cmd = data_from_man_page[0][BashParser.INDEX_CMD][BashParser.INDEX_VALUE]
                # consoleUtils.ConsoleUtils.open_interactive_man_page(cmd)
                # return ""
            # -> command
            elif c == Keys.KEY_RIGHT:
                self.context_shift.shift_context_right()
            # <- command
            elif c == Keys.KEY_LEFT:
                self.context_shift.shift_context_left()
            elif c == Keys.KEY_DOWN:
                page_info.shift_blocks_down()
            elif c == Keys.KEY_UP:
                page_info.shift_blocks_up()
            elif c in Keys.KEYS_EDIT:
                res = loop_edit.run_loop_edit_command(page_info.get_blocks_shift(), bash_parser_thread)
                if res[0]:
                    return [False, "command_update", res[1]]
            elif c == Keys.KEY_TAG:  # "#"
                if loop_edit.run_loop_edit_tags(bash_parser_thread):
                    return [False, "update"]
            elif c == Keys.KEY_AT:  # "@"
                if loop_edit.run_loop_edit_description(page_info.get_blocks_shift(), bash_parser_thread):
                    return [False, "update"]
            elif c == Keys.KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                self.search_t.set_max_x(self.drawer.get_max_x())
            else:
                logging.error("input not handled: %s" % repr(c))

