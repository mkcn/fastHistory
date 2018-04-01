#!/usr/bin/python

import sys
import os
import logging
from database.dataManager import DataManager

LOG_FILE_NAME = "data/smartHistory.log"
DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(input_cmd_str, project_dir):
	"""
	take input and show the filtered list of command to select

	:param project_dir: 	path of the project
	:param input_cmd_str:	input cmd
	:return:
	"""
	# local import to not affect the response time of the bash command
	from console.consoleUtils import ConsoleUtils
	from pick.picker import Picker

	logging.info("search request: '" + input_cmd_str + "'")
	# set SIGINT handler
	ConsoleUtils.handle_close_signal()
	# create data manger obj
	data_manager = DataManager(project_dir, DATABASE_MODE)
	# open picker to select from history
	picker = Picker(data_manager, search_text=input_cmd_str)
	selected_option, index = picker.start()
	selected_string = selected_option[0]
	# show selected cmd
	ConsoleUtils.fill_terminal_input(selected_string)


def handle_add_request(input_cmd_str, project_dir, feedback=False):
	"""
	take input and add store it

	:param project_dir: 	path of the project
	:param input_cmd_str:	input cmd
	:param feedback:		if true prints feedback message in the console, otherwise hides all
	:return:
	"""
	# local import to not affect the response time of the bash commandv
	from parser import tagParser
	from console.loggerBash import log_on_console_info, log_on_console_error

	# define log class
	logging.info("add request: '" + input_cmd_str + "'")

	# if no privacy mode add the command
	if not tagParser.TagParser.is_privacy_mode_enable(input_cmd):
		# parse tags and store the cmd
		parser_res = tagParser.TagParser.parse_cmd(input_cmd_str)

		cmd = parser_res[0]
		description = parser_res[1]
		tags = parser_res[2]

		data_retriever = DataManager(project_dir, DATABASE_MODE)
		data_retriever.add_new_element(cmd, description, tags)
		logging.info("command: added")
		if feedback:
			log_on_console_info("command: added")
	else:
		logging.info("PRIVACY mode ENABLED")
		if feedback:
			log_on_console_info("PRIVACY mode ENABLED")


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	# check number of parameters
	if len(sys.argv) == 3:
		project_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
		logging.basicConfig(filename=project_dir + LOG_FILE_NAME, level=logging.DEBUG)
		logging.debug("bash input: " + str(sys.argv))

		mode = str(sys.argv[1])
		input_cmd = str(sys.argv[2])
		if mode == "search":
			handle_search_request(input_cmd, project_dir)
		elif mode == "add":
			handle_add_request(input_cmd, project_dir, True)
		elif mode == "add-silent" and len(input_cmd) > 0:
			handle_add_request(input_cmd, project_dir)
	else:
		# TODO print usage
		pass

