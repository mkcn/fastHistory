# -*-coding:utf-8-*-

import curses
import logging

from fastHistory.pick.drawer import Drawer
from fastHistory.pick.loopSelectFavourites import LoopSelectFavourites
from fastHistory.pick.loopSelectTLDR import LoopSelectTLDR
from fastHistory.pick.textManager import TextManager


class Picker(object):
    """
    Class used to show the available value and select one (or more)
    """
    SEARCH_FIELD_MARGIN = 23

    SEARCH_TYPE_FAVOURITE = 0
    SEARCH_TYPE_HISTORY = 1  # not implemented
    SEARCH_TYPE_TLDR = 2

    def __init__(self, data_manager, theme, last_column_size, is_tldr_search=False, is_history_search=False, search_text="", multi_select=False):
        """
        initialize variables and get filtered list starting options to show
        :param data_manager          the data manager object to retrieve data
        :param search_text:         (optional) if defined the results will be filtered with this text, default emtpy string
        :param multi_select:        (optional) if true its possible to select multiple values by hitting SPACE, defaults to False
        """
        self.theme = theme
        self.search_text = search_text
        self.multi_select = multi_select
        self.data_manager = data_manager
        self.last_column_size = last_column_size

        if is_tldr_search:
            self.search_type = self.SEARCH_TYPE_TLDR
        elif is_history_search:
            self.search_type = self.SEARCH_TYPE_HISTORY
        else:
            self.search_type = self.SEARCH_TYPE_FAVOURITE

        self.drawer = None

    def start(self):
        return curses.wrapper(self._start)

    def _start(self, screen):
        self.drawer = Drawer(screen, self.theme, TextManager.TEXT_TOO_LONG)
        return self.run_ui

    @property
    def run_ui(self):
        """
        manage the switch between tabs:
            - tab1: loop select favourite commands
            - tab2: loop select TDLR commands
        :return:
        """
        search_t = TextManager(text=self.search_text,
                               use_lower=True,
                               max_x=self.drawer.get_max_x(),
                               margin_x=self.SEARCH_FIELD_MARGIN)
        cached_in_memory_tldr_pages = {}

        while 1:
            if self.search_type == self.SEARCH_TYPE_FAVOURITE:
                loop_select = LoopSelectFavourites(drawer=self.drawer,
                                                   data_manager=self.data_manager,
                                                   search_t=search_t,
                                                   last_column_size=self.last_column_size,
                                                   multi_select=self.multi_select)
                res = loop_select.run_loop_select()
            elif self.search_type == self.SEARCH_TYPE_HISTORY:
                logging.warning("search_type not implemented yet: %s" % self.search_type)
                return None
            elif self.search_type == self.SEARCH_TYPE_TLDR:
                loop_tldr = LoopSelectTLDR(drawer=self.drawer, search_text=search_t)
                res = loop_tldr.run_loop_tldr(cached_in_memory_tldr_pages)
            else:
                logging.error("unknown search_type: %s" % self.search_type)
                return None

            if res[0]:
                return res[1]
            else:
                self.search_type = res[1]

