#!/usr/bin/python

import sys
import os
import logging
from config.configReader import ConfigReader
from database.dataManager import DataManager
from console import loggerBash


PATH_LOG_FILE = "data/history.log"
PATH_DATABASE_FILE = "data/history.db"
PATH_CONFIGURATION_FILE = "config/config.ini"

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(input_cmd_str, project_directory, theme, last_column_size):
	"""
	take input and show the filtered list of command to select

	:param project_directory: 	path of the project
	:param input_cmd_str:		input cmd
	:param logger_console:			logger for terminal console
	:param theme:				theme (colors)
	:param last_column_size:	size of last column (percentage)
	:return:
	"""
	# local import to load this module only in case of a search command
	from console.consoleUtils import ConsoleUtils
	from pick.picker import Picker

	logging.debug("search request: '" + input_cmd_str + "'")
	# set SIGINT handler
	ConsoleUtils.handle_close_signal()
	# create data manger obj
	data_manager = DataManager(project_directory + PATH_DATABASE_FILE, DATABASE_MODE)

	# open picker to select from history
	picker = Picker(data_manager, theme=theme, last_column_size=last_column_size, search_text=input_cmd_str)
	selected_option = picker.start()

	# inject into the terminal the selected command
	try:
		ConsoleUtils.fill_terminal_input(selected_option)
	except:
		logging.debug("your terminal does not support automatic input injection")
		logger_console.log_on_console_error("Your terminal does not support automatic input injection")
		logger_console.log_on_console_error("Please manually copy and paste the selected command")
		logger_console.log_on_console("")
		logger_console.log_on_console(selected_option)
		logger_console.log_on_console("")


def handle_add_request(input_cmd_str, project_directory, error_feedback=False):
	"""
	take input and add store it

	:param project_directory: 	path of the project
	:param input_cmd_str:		input cmd
	:param logger_console:			logger for terminal console
	:param error_feedback:		if true print error messages in the console, otherwise hide them
	:return:
	"""
	# local import to load this module only in case of an 'add' commands
	from parser.tagParser import TagParser

	# define log class
	logging.debug("add request: '" + input_cmd_str + "'")

	# parse tags and store the cmd
	parser_res = TagParser.parse_cmd(input_cmd_str)

	if parser_res is None:
		if error_feedback:
			logger_console.log_on_console_error("Wrong input")
			logger_console.log_on_console_info("Syntax : command [#[tag [#tag ...]][@description]]")
			logger_console.log_on_console_info("Example: ls -la #tag1 #tag2 #tag2 @a long description")
	else:
		cmd = parser_res[TagParser.INDEX_CMD]
		description = parser_res[TagParser.INDEX_DESC]
		tags = parser_res[TagParser.INDEX_TAGS]

		data_manager = DataManager(project_directory + PATH_DATABASE_FILE, DATABASE_MODE)
		stored = data_manager.add_new_element(cmd, description, tags)
		if stored:
			logging.info("command added")
			logger_console.log_on_console_info("new command:  " + cmd)
			if tags and len(tags) > 0 and tags[0] != "":
				str_tags = ""
				for tag in tags:
					str_tags += logger_console.tag_colored + tag + " "
				logger_console.log_on_console_info("tags:         " + str_tags)
			if description and len(description) > 0:
				logger_console.log_on_console_info("description:  %s%s" % (logger_console.desc_colored, description))
		else:
			logging.error("store command failed")
			logger_console.log_on_console_info("store command failed. please check your log file: " + PATH_LOG_FILE)


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""

	logger_console = loggerBash.LoggerBash()

	try:
		# check number of parameters
		if len(sys.argv) == 3:
			# get execution path
			project_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

			# load config file
			configReader = ConfigReader(project_dir + PATH_CONFIGURATION_FILE)
			if configReader.check_config():
				# set color for console logs
				logger_console.set_theme(configReader.get_theme())

				# set logging (this setting is applied globally for all logging calls from now on)
				logging.basicConfig(filename=project_dir + PATH_LOG_FILE, level=configReader.get_log_level())
				logging.debug("bash input: %s" % str(sys.argv))

				mode = str(sys.argv[1])
				input_cmd = str(sys.argv[2])
				if mode == "search":
					handle_search_request(input_cmd,
										  project_dir,
										  configReader.get_theme(),
										  configReader.get_last_column_size())
				elif mode == "add":
					handle_add_request(input_cmd, project_dir)
				elif mode == "add-explicit" and len(input_cmd) > 0:
					handle_add_request(input_cmd, project_dir, error_feedback=True)
				else:
					logger_console.log_on_console_error("'mode' parameter unknown")
			else:
				logger_console.log_on_console_error("error in config file: %s" % project_dir + PATH_CONFIGURATION_FILE)
				logger_console.log_on_console_error("error details: %s" % configReader.get_error_msg())
		else:
			logger_console.log_on_console_error("wrong number of parameters")
			pass
	except Exception as e:
		logger_console.log_on_console_error("general error detected: %s" % str(e))


