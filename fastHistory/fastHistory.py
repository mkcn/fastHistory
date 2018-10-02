#!/usr/bin/python

import sys
import os
import logging
from database.dataManager import DataManager
from console.loggerBash import log_on_console_info, log_on_console_error, log_on_console


LOG_FILE_NAME = "data/history.log"
DATABASE_FILENAME = "data/history.db"

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(input_cmd_str, project_directory):
	"""
	take input and show the filtered list of command to select

	:param project_directory: 	path of the project
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
	data_manager = DataManager(project_directory + DATABASE_FILENAME, DATABASE_MODE)

	# open picker to select from history
	picker = Picker(data_manager, search_text=input_cmd_str)

	selected_option = picker.start()

	# show selected cmd
	try:
		ConsoleUtils.fill_terminal_input(selected_option)
	except:
		logging.error("your terminal does not support automatic input injection")
		log_on_console_error("Your terminal does not support automatic input injection")
		log_on_console("")
		log_on_console(selected_option)
		log_on_console("")


def handle_add_request(input_cmd_str, project_directory, feedback=False):
	"""
	take input and add store it

	:param project_directory: 	path of the project
	:param input_cmd_str:	input cmd
	:param feedback:		if true prints feedback message in the console, otherwise hides all
	:return:
	"""
	# local import to not affect the response time of the bash command
	from parser.tagParser import TagParser

	# define log class
	logging.debug("add request: '" + input_cmd_str + "'")

	# parse tags and store the cmd
	parser_res = TagParser.parse_cmd(input_cmd_str)

	if parser_res is None:
		if feedback:
			log_on_console_error("Wrong input")
			log_on_console_info("Syntax : hadd command [#[tag [#tag ...]][@description]]")
			log_on_console_info("Example: hadd ls -la #tag1 #tag2 #tag2 @a long description")
			# TODO create and print help page
	else:
		cmd = parser_res[TagParser.INDEX_CMD]
		description = parser_res[TagParser.INDEX_DESC]
		tags = parser_res[TagParser.INDEX_TAGS]

		# TODO idea to test
		if description is None:
			# 1) extract cmd from input string (without tags and description)
			# 2) get meaning for the cmd from man page
			# 3) set it as description
			pass

		data_manager = DataManager(project_directory + DATABASE_FILENAME, DATABASE_MODE)
		stored = data_manager.add_new_element(cmd, description, tags)
		if stored:
			logging.info("command added")
			if feedback:
				log_on_console_info("command added: \t" + cmd)
				if tags and len(tags) > 0:
					log_on_console_info("tags: \t\t" + str(tags))
				if description and len(description) > 0:
					log_on_console_info("description: \t" + description)
		else:
			logging.info("command: fail")
			if feedback:
				log_on_console_info("command add fail, please check your log file")


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

