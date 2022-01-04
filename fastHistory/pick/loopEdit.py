import logging

from fastHistory import DataManager
from fastHistory.parser.inputParser import InputParser
from fastHistory.pick.keys import Keys
from fastHistory.pick.textManager import TextManager


class LoopEdit(object):

    EDIT_FIELD_MARGIN = 4
    TEXT_NOT_ALLOWED_STR = "text not allowed"

    def __init__(self, current_selected_option, drawer, data_manager, context_shift, multi_select=False):

        self.drawer = drawer
        self.data_manager = data_manager
        self.context_shift = context_shift
        self.current_selected_option = current_selected_option

    def run_loop_edit_command(self, blocks_shift, bash_parser_thread):
        """
        loop to capture user input keys to interact with the "edit command" page

        :return:    [False, None] if no change has been done, [True, <new_command_str>] otherwise]
        """
        # import this locally to improve performance when the program is loaded
        from fastHistory.pick.pageEditCommand import PageEditCommand
        page_command = PageEditCommand(self.drawer,
                                       option=self.current_selected_option,
                                       search_filters=self.data_manager.get_search_filters(),
                                       context_shift=self.context_shift,
                                       blocks_shift=blocks_shift)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        command_t = TextManager(self.current_selected_option[DataManager.OPTION.INDEX_CMD],
                                max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        input_error_msg = None

        while True:
            if page_command.has_minimum_size():
                page_command.clean_page()
                page_command.draw_page_edit(command_text=command_t.get_text_to_print(),
                                            command_cursor_index=command_t.get_cursor_index_to_print(),
                                            input_error_msg=input_error_msg,
                                            data_from_man_page=bash_parser_thread.get_result())
                page_command.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char(multi_threading_mode=bash_parser_thread.is_alive())

            if c == Keys.KEY_TIMEOUT:
                continue
            # save and exit
            elif c in Keys.KEYS_ENTER:
                new_command = command_t.get_text()
                if current_command == new_command:
                    return [False, None]
                else:
                    is_valid_command = InputParser.is_cmd_str_valid(new_command)
                    if is_valid_command:
                        if self.data_manager.update_command(current_command, new_command):
                            return [True, new_command]
                        else:
                            msg = "database error during saving, please try again"
                            logging.error(msg)
                            input_error_msg = msg
                    else:
                        input_error_msg = "no tags and description are allowed here"

            # exit without saving
            elif c == Keys.KEY_TAB or c == Keys.KEY_SHIFT_TAB or c == Keys.KEY_ESC:
                return [False, None]
            # -> command
            elif c == Keys.KEY_RIGHT:
                if command_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    command_t.move_cursor_right()
                # <- command
            elif c == Keys.KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not command_t.is_cursor_at_the_beginning():
                    command_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in Keys.KEYS_DELETE:
                command_t.delete_char()
                input_error_msg = None
            # move cursor to the beginning
            elif c == Keys.KEY_START or c == Keys.KEY_CTRL_A:
                command_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == Keys.KEY_END or c == Keys.KEY_CTRL_E:
                command_t.move_cursor_to_end()
            elif c == Keys.KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                command_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif c == Keys.KEY_CTRL_U:
                command_t.set_text("")
            elif type(c) is str:
                command_t.add_string(c, self.data_manager.get_forbidden_chars())
                input_error_msg = None
            else:
                logging.error("input not handled: %s" % repr(c))

    def run_loop_edit_description(self, blocks_shift, bash_parser_thread):
        """
        loop to capture user input keys to interact with the "add description" page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from fastHistory.pick.pageEditDescription import PageEditDescription
        page_desc = PageEditDescription(self.drawer,
                                        option=self.current_selected_option,
                                        search_filters=self.data_manager.get_search_filters(),
                                        context_shift=self.context_shift,
                                        blocks_shift=blocks_shift)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        description_t = TextManager(InputParser.DESCRIPTION_SIGN +
                                    self.current_selected_option[DataManager.OPTION.INDEX_DESC],
                                    max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        input_error_msg = None

        while True:
            if page_desc.has_minimum_size():
                page_desc.clean_page()
                page_desc.draw_page_edit(description_text=description_t.get_text_to_print(),
                                         description_cursor_index=description_t.get_cursor_index_to_print(),
                                         input_error_msg=input_error_msg,
                                         data_from_man_page = bash_parser_thread.get_result())
                page_desc.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char(multi_threading_mode=bash_parser_thread.is_alive())

            if c == Keys.KEY_TIMEOUT:
                continue
            # save and exit
            elif c in Keys.KEYS_ENTER:
                new_description = InputParser.parse_description(description_t.get_text())
                if new_description is not None:
                    if self.data_manager.update_description(current_command, new_description):
                        return True
                    else:
                        msg = "database error during saving, please try again"
                        logging.error(msg)
                        input_error_msg = msg
                else:
                    input_error_msg = self.TEXT_NOT_ALLOWED_STR

            # exit without saving
            elif c == Keys.KEY_TAB or c == Keys.KEY_SHIFT_TAB or c == Keys.KEY_ESC:
                return False
            # -> command
            elif c == Keys.KEY_RIGHT:
                if description_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    description_t.move_cursor_right()
                # <- command
            elif c == Keys.KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not description_t.is_cursor_at_the_beginning():
                    description_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
            # delete a char of the search
            elif c in Keys.KEYS_DELETE:
                description_t.delete_char()
                if input_error_msg is not None:
                    new_description = InputParser.parse_description(description_t.get_text())
                    if new_description is None:
                        input_error_msg = self.TEXT_NOT_ALLOWED_STR
                    else:
                        input_error_msg = None
            # move cursor to the beginning
            elif c == Keys.KEY_START or c == Keys.KEY_CTRL_A:
                description_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == Keys.KEY_END or c == Keys.KEY_CTRL_E:
                description_t.move_cursor_to_end()
            elif c == "#":  # Keys.KEY_RESIZE:
                # this occurs when the console size changes
                self.drawer.reset()
                description_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif c == Keys.KEY_CTRL_U:
                description_t.set_text("")
            elif type(c) is str:
                description_t.add_string(c, self.data_manager.get_forbidden_chars())
                new_description = InputParser.parse_description(description_t.get_text())
                if new_description is None:
                    input_error_msg = self.TEXT_NOT_ALLOWED_STR
                else:
                    input_error_msg = None
            else:
                logging.error("input not handled: %s" % repr(c))

    def run_loop_edit_tags(self, bash_parser_thread):
        """
        loop to capture user input keys to interact with the "add tag" page

        :return:
        """
        # import this locally to improve performance when the program is loaded
        from fastHistory.pick.pageEditTags import PageEditTags
        page_tags = PageEditTags(self.drawer,
                                 option=self.current_selected_option,
                                 search_filters=self.data_manager.get_search_filters(),
                                 context_shift=self.context_shift)

        current_command = self.current_selected_option[DataManager.OPTION.INDEX_CMD]
        new_tags = self.current_selected_option[DataManager.OPTION.INDEX_TAGS]
        new_tags_str = ""
        for tag in new_tags:
            if len(tag) > 0:
                new_tags_str += InputParser.TAG_SIGN + tag + " "

        new_tags_t = TextManager(new_tags_str, max_x=self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
        new_tags_t.add_string(InputParser.TAG_SIGN, self.data_manager.get_forbidden_chars())

        input_error_msg = None

        while True:
            if page_tags.has_minimum_size():
                page_tags.clean_page()
                page_tags.draw_page_edit(tags_text=new_tags_t.get_text_to_print(),
                                         tags_cursor_index=new_tags_t.get_cursor_index_to_print(),
                                         input_error_msg=input_error_msg,
                                         data_from_man_page=bash_parser_thread.get_result())
                page_tags.refresh_page()

            # wait for char
            c = self.drawer.wait_next_char(multi_threading_mode=bash_parser_thread.is_alive())

            if c == Keys.KEY_TIMEOUT:
                continue
            elif c in Keys.KEYS_ENTER:
                new_tags_array = InputParser.parse_tags_str(new_tags_t.get_text())
                if new_tags_array is not None:
                    if self.data_manager.update_tags(current_command, new_tags_array):
                        return True
                    else:
                        msg = "database error during saving, please try again"
                        logging.error(msg)
                        input_error_msg = msg
                else:
                    input_error_msg = self.TEXT_NOT_ALLOWED_STR
            # exit without saving
            # TODO fix return if "alt+char" is pressed
            elif c == Keys.KEY_TAB or c == Keys.KEY_SHIFT_TAB or c == Keys.KEY_ESC:
                return False
            # -> command
            elif c == Keys.KEY_RIGHT:
                if new_tags_t.is_cursor_at_the_end():
                    self.context_shift.shift_context_right()
                else:
                    # move the search cursor one position right (->)
                    new_tags_t.move_cursor_right()
                # <- command
            elif c == Keys.KEY_LEFT:
                if not self.context_shift.is_context_index_zero():
                    self.context_shift.shift_context_left()
                elif not new_tags_t.is_cursor_at_the_beginning():
                    new_tags_t.move_cursor_left()
                else:
                    # do nothing, the cursor is already on the position 0
                    pass
                    # delete a char of the search
            elif c in Keys.KEYS_DELETE:
                # the delete is allowed if the search text is not empty and if
                if new_tags_t.delete_char():
                    self.context_shift.reset_context_shifted()
                if input_error_msg is not None:
                    new_tags_array = InputParser.parse_tags_str(new_tags_t.get_text())
                    if new_tags_array is None:
                        input_error_msg = self.TEXT_NOT_ALLOWED_STR
                    else:
                        input_error_msg = None
            # move cursor to the beginning
            elif c == Keys.KEY_START or c == Keys.KEY_CTRL_A:
                new_tags_t.move_cursor_to_start()
                self.context_shift.reset_context_shifted()
            # move cursor to the end
            elif c == Keys.KEY_END or c == Keys.KEY_CTRL_E:
                new_tags_t.move_cursor_to_end()
            # this occurs when the console size changes
            elif c == Keys.KEY_RESIZE:
                self.drawer.reset()
                new_tags_t.set_max_x(self.drawer.get_max_x() - self.EDIT_FIELD_MARGIN)
            elif c == Keys.KEY_CTRL_U:
                new_tags_t.set_text("")
            elif type(c) is str:
                new_tags_t.add_string(c, self.data_manager.get_forbidden_chars())
                new_tags_array = InputParser.parse_tags_str(new_tags_t.get_text())
                if new_tags_array is None:
                    input_error_msg = self.TEXT_NOT_ALLOWED_STR
                else:
                    input_error_msg = None
            else:
                logging.error("input not handled: %s" % repr(c))
