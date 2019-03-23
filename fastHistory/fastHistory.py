#!/usr/bin/python

import sys
import os
import logging
from config.configReader import ConfigReader
from database.dataManager import DataManager
from console.consoleUtils import ConsoleUtils
from console import loggerBash


PATH_LOG_FILE = "../data/fh.log"
PATH_DATABASE_FILE = "../data/fh_v1.db"
PATH_OLD_DATABASE_FILES = ["data/history.db"]
PATH_CONFIGURATION_FILE = "../fastHistory.conf"

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(input_cmd_str, project_directory, theme, last_column_size):
	"""
	take input and show the filtered list of command to select

	:param input_cmd_str:		input cmd
	:param project_directory: 	path of the project
	:param theme:				theme (colors)
	:param last_column_size:	size of last column (percentage)
	:return:
	"""
	# local import to load this module only in case of a search command
	from pick.picker import Picker
	logging.debug("search request: '" + input_cmd_str + "'")
	# create data manger obj
	data_manager = DataManager(project_directory, PATH_DATABASE_FILE, PATH_OLD_DATABASE_FILES, DATABASE_MODE)

	# open picker to select from history
	picker = Picker(data_manager, theme=theme, last_column_size=last_column_size, search_text=input_cmd_str)
	selected_option = picker.start()

	# inject into the terminal the selected command
	try:
		ConsoleUtils.fill_terminal_input(selected_option)
	except:
		logging.debug("your terminal does not support automatic input injection")
		logger_console.log_on_console_error("your terminal does not support automatic input injection")
		logger_console.log_on_console_error("please manually copy and paste the selected command")
		logger_console.log_on_console("")
		logger_console.log_on_console(selected_option)
		logger_console.log_on_console("")


def handle_add_request(input_cmd_str, project_directory, error_feedback=False):
	"""
	take input and add store it

	:param input_cmd_str:		input cmd
	:param project_directory: 	path of the project
	:param error_feedback:		if true print error messages in the console, otherwise hide them
	:return:
	"""
	# local import to load this module only in case of an 'add' commands
	from parser.inputParser import InputParser

	# define log class
	logging.debug("add request: '" + input_cmd_str + "'")

	# parse tags and store the cmd
	parser_res = InputParser.parse_input(input_cmd_str)

	if parser_res is None:
		if error_feedback:
			logger_console.log_on_console_error("wrong input")
			logger_console.log_on_console_info("syntax : f-add <command> #[<tag> [#<tag> ...]][@<description>]")
			logger_console.log_on_console_info("example: f-add ls -la #tag1 #tag2 #tag2 @a long description")
	else:
		cmd = parser_res.get_main_str()
		description = parser_res.get_description_str()
		tags = parser_res.get_tags(strict=True)

		data_manager = DataManager(project_directory, PATH_DATABASE_FILE, PATH_OLD_DATABASE_FILES, DATABASE_MODE)
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
			logger_console.log_on_console_info("store command failed, please check your log file: %s" %
											os.path.abspath(project_directory + PATH_LOG_FILE))


def handle_import_db(db_abs_path, project_directory):
	"""
	import data from external database
	:param db_abs_path:			absolute path database file
	:param project_directory:	path of the project
	:return:
	"""
	logging.info("import database: %s" % str(db_abs_path))
	logger_console.log_on_console_info("import database: %s" % str(db_abs_path))
	data_manager = DataManager(project_directory, PATH_DATABASE_FILE, PATH_OLD_DATABASE_FILES, DATABASE_MODE)
	imported_items = data_manager.import_data_to_db(db_abs_path)
	if imported_items >= 0:
		logging.info("import database: %s elements imported" % str(imported_items))
		logger_console.log_on_console_info("import database: %s elements imported" % str(imported_items))
		return
	elif not os.path.isfile(db_abs_path):
		logging.error("import database: fail")
		logger_console.log_on_console_error("input file does not exist: %s" % str(db_abs_path))
	else:
		logging.error("import database: fail")
		logger_console.log_on_console_error("please check your log file: %s" %
											os.path.abspath(project_directory + PATH_LOG_FILE))
	# show correct usage
	logger_console.log_on_console_info("syntax : f-import FILENAME")
	logger_console.log_on_console_info("example: f-import fastHistory_2018-08-09.db")


def handle_export_db(output_path, project_directory):
	"""
	export all database
	:param output_path:			output file
	:param project_directory:	path of the project
	:return:
	"""
	try:
		from shutil import copyfile

		logging.info("export output: %s " % str(output_path))
		logger_console.log_on_console_info("export output: %s " % str(output_path))
		if os.path.isfile(output_path):
			answer = input("output file already exits, overwrite it? [y/N] ")
			if answer.lower() != "y":
				logger_console.log_on_console_error("export database cancel")
				return
		if os.path.isdir(output_path):
			logger_console.log_on_console_error("error: output path cannot be a directory")
			return
		copyfile(project_directory + PATH_DATABASE_FILE, output_path)
		logging.info("export output exported")
		logger_console.log_on_console_info("database file exported")
	except Exception as ex:
		logging.error("export database error: %s" % str(ex))
		logger_console.log_on_console_error("error: please check your log file: %s" %
											os.path.abspath(project_directory + PATH_LOG_FILE))
		logger_console.log_on_console_info("syntax : f-export [OUTPUT]")
		logger_console.log_on_console_info("example: f-export fastHistory_virtual_machine.db")


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	logger_console = loggerBash.LoggerBash()
	try:
		# set SIGINT handler
		ConsoleUtils.handle_close_signal()

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
					handle_search_request(input_cmd, project_dir, configReader.get_theme(), configReader.get_last_column_size())
				elif mode == "add":
					handle_add_request(input_cmd, project_dir)
				elif mode == "add-explicit" and len(input_cmd) > 0:
					handle_add_request(input_cmd, project_dir, error_feedback=True)
				elif mode == "import":
					handle_import_db(input_cmd, project_dir)
				elif mode == "export":
					handle_export_db(input_cmd, project_dir)
				else:
					logger_console.log_on_console_error("'mode' parameter unknown. check your '.bashrc' file and reload bash")
			else:
				logger_console.log_on_console_error("error in config file: %s" % project_dir + PATH_CONFIGURATION_FILE)
				logger_console.log_on_console_error("error details: %s" % configReader.get_error_msg())
		else:
			logger_console.log_on_console_error("wrong number of parameters")
			pass
	except Exception as e:
		logger_console.log_on_console_error("general error detected: %s" % str(e))


