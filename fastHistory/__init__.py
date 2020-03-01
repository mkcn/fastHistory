#!/usr/bin/python
import sys
import os
import logging
from fastHistory.config.configReader import ConfigReader
from fastHistory.database.dataManager import DataManager
from fastHistory.console.consoleUtils import ConsoleUtils
from fastHistory.console import loggerBash

PATH_DATA_FOLDER = "/.local/share/fastHistory/"
PATH_LOG_FILE = "fh.log"
PATH_DATABASE_FILE = "fh_v1.db"
PATH_CONFIGURATION_FILE = "fastHistory.conf"
PATH_OLD_DATABASE_FILES = ["history.db"]

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(logger_console, input_cmd_str, project_directory, theme, last_column_size):
	"""
	take input and show the filtered list of command to select

	:param input_cmd_str:		input cmd
	:param project_directory: 	path of the project
	:param theme:				theme (colors)
	:param last_column_size:	size of last column (percentage)
	:return:
	"""
	# local import to load this module only in case of a search command
	from fastHistory.pick.picker import Picker
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


def handle_add_request(logger_console, input_cmd_str, project_directory, error_feedback=False):
	"""
	take input and add store it

	:param input_cmd_str:		input cmd
	:param project_directory: 	path of the project
	:param error_feedback:		if true print error messages in the console, otherwise hide them
	:return:
	"""
	# local import to load this module only in case of an 'add' commands
	from fastHistory.parser.inputParser import InputParser

	# define log class
	logger_console.log_on_console_info("add request: '" + input_cmd_str + "'")
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


def handle_import_db(logger_console, db_abs_path, project_directory):
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


def handle_export_db(logger_console, output_path, project_directory):
	"""
	export all database
	:param output_path:			output file
	:param project_directory:	path of the project
	:return:
	"""
	try:
		from shutil import copyfile
		from datetime import date
		
		if output_path is None:
			current_date = date.today()
			output_path = os.getcwd() + "/fastHistory_" +  current_date.strftime("%Y-%m-%d") + ".db"

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


def edit_config_file(logger_console, project_dir):
	config_file=project_dir + PATH_CONFIGURATION_FILE
	logger_console.log_on_console_info("to change the configuration file you can use the following injected command")
	try:
		ConsoleUtils.fill_terminal_input("nano "+config_file)
	except:
		logger_console.log_on_console_error("your terminal does not support automatic input injection")
		logger_console.log_on_console_error("please edit the configuration file manually")
		logger_console.log_on_console(config_file)


   
def main():
	logger_console = loggerBash.LoggerBash()
	#try:
	# set SIGINT handler
	ConsoleUtils.handle_close_signal()

	# get execution path
	project_dir = os.environ['HOME'] + PATH_DATA_FOLDER
		
	# load config file
	configReader = ConfigReader(project_dir, PATH_CONFIGURATION_FILE)
	if configReader.check_config():
		# set color for console logs
		logger_console.set_theme(configReader.get_theme())

		# set logging (this setting is applied globally for all logging calls from now on)
		logging.basicConfig(filename=project_dir + PATH_LOG_FILE, level=configReader.get_log_level())
		logging.debug("bash input: %s" % str(sys.argv))
				
		args_len = len(sys.argv)
		# check number of parameters
		if args_len == 1:
			input_cmd = ""
			handle_search_request(logger_console, input_cmd, project_dir, configReader.get_theme(), configReader.get_last_column_size())
		elif args_len >= 2:
			arg1 = str(sys.argv[1])
			if (arg1 == "--add-from-bash") and args_len == 3:
				input_cmd = " ".join(sys.argv[2:]).strip()
				handle_add_request(logger_console, input_cmd, project_dir)
			elif (arg1 == "--add-from-bash-explicit") and args_len == 3:
				input_cmd = " ".join(sys.argv[2:]).strip()
				handle_add_request(logger_console, input_cmd, project_dir, error_feedback=True)
			elif (arg1 == "--search-from-bash") and args_len == 3:
				input_cmd = " ".join(sys.argv[2:]).strip()
				handle_search_request(logger_console, input_cmd, project_dir, configReader.get_theme(), configReader.get_last_column_size())
			elif (arg1 == "--config") and args_len == 2: # TODO , this should be reachable even if the file is broken
				edit_config_file(logger_console,project_dir)
			elif (arg1 == "-i" or arg1 == "--import") and args_len == 3:
				import_file = sys.argv[2]
				handle_import_db(logger_console, import_file, project_dir)
			elif (arg1 == "-e" or arg1 == "--export") and args_len == 3:
				output_path = sys.argv[2]
				handle_export_db(logger_console, output_path, project_dir)
			elif (arg1 == "-e" or arg1 == "--export") and args_len == 2:
				handle_export_db(logger_console, None, project_dir)
			elif (arg1 == "-h" or arg1 == "--help") and args_len == 2:
				# TODO print help
				logger_console.log_on_console_error("help not yet implemented")
			else:
				input_cmd = " ".join(sys.argv[1:])
				handle_search_request(logger_console, input_cmd, project_dir, configReader.get_theme(), configReader.get_last_column_size())
	elif (False):
		# TODO manage "--setup" and "--config"
		pass
	else:
		logger_console.log_on_console_error("error: %s" % configReader.get_error_msg())
		from fastHistory.config.setupManager import SetupManager
		setupManager = SetupManager(logger_console, project_dir, PATH_CONFIGURATION_FILE)
		setupManager.auto_setup()
	
		
	#epxcept Exception as e:
	#	logger_console.log_on_console_error("general error detected: %s" % str(e))


def f():
	main()

if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	print("the main of fastHistory is not enabled, please use the 'f()' function")
	
