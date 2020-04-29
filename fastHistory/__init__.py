#!/usr/bin/python
import sys
import os
import logging
from fastHistory.config.configReader import ConfigReader
from fastHistory.database.dataManager import DataManager
from fastHistory.console.consoleUtils import ConsoleUtils
from fastHistory.console import loggerBash

FAST_HISTORY_EXECUTABLE="f"
PATH_DATA_FOLDER = "/.local/share/fastHistory/"
NAME_LOG_FILE = "fh.log"
NAME_DATABASE_FILE = "fh_v1.db"
NAME_CONFIGURATION_FILE = "fastHistory.conf"
NAME_VERSION_FILE = "version.txt"
NAME_OLD_DATABASE_FILES = [""]

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(logger_console, input_cmd_str, path_data_folder, theme, last_column_size):
	"""
	take input and show the filtered list of command to select

	:return:
	"""
	# local import to load this module only in case of a search command
	from fastHistory.pick.picker import Picker
	if input_cmd_str is None:
		logger_console.log_on_console_error("cannot read parameters from bash, please try to restart your terminal")
	else:
		logging.debug("search request parameters: '" + str(input_cmd_str) + "'")
		# create data manger obj
		data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, NAME_OLD_DATABASE_FILES, DATABASE_MODE)

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


def handle_add_request(logger_console, input_cmd_str, path_data_folder, error_feedback=False):
	"""
	take input and add store it

	:return:
	"""
	# local import to load this module only in case of an 'add' commands
	from fastHistory.parser.inputParser import InputParser

	# define log class
	logging.debug("add request: '" + input_cmd_str + "'")

	# parse tags and store the cmd
	parser_res = InputParser.parse_input(input_cmd_str)

	if parser_res is None:
		if error_feedback:
			logger_console.log_on_console_error("wrong input")
			logger_console.log_on_console_info("syntax  :  f --add <command> #[<tag> [#<tag> ...]][@<description>]")
			logger_console.log_on_console_info("examples:  f --add ls -la #")
			logger_console.log_on_console_info("           f --add ls -la #list @show files")
			logger_console.log_on_console_info("syntax 2:  #<command> #[<tag> [#<tag> ...]][@<description>]")
			logger_console.log_on_console_info("examples:  #ls -la #")
			logger_console.log_on_console_info("           #ls -la #list @show files")
	else:
		cmd = parser_res.get_main_str()
		description = parser_res.get_description_str()
		tags = parser_res.get_tags(strict=True)

		data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, NAME_OLD_DATABASE_FILES, DATABASE_MODE)
		stored = data_manager.add_new_element(cmd, description, tags)
		if stored:
			logging.info("command added")
			logger_console.log_on_console_info("command:    '%s'" % cmd)
			if tags and len(tags) > 0 and tags[0] != "":
				str_tags = ""
				for tag in tags:
					str_tags += logger_console.tag_colored + tag + " "
				logger_console.log_on_console_info("tags:        %s" % str_tags)
			if description and len(description) > 0:
				logger_console.log_on_console_info("description: %s%s" % (logger_console.desc_colored, description))
		else:
			logging.error("store command failed")
			logger_console.log_on_console_info("store command failed, please check your log file: %s" %
											   os.path.abspath(path_data_folder + NAME_LOG_FILE))


def handle_import_db(logger_console, db_abs_path, path_data_folder):
	"""
	import data from external database
	"""
	logging.info("import database: %s" % str(db_abs_path))
	logger_console.log_on_console_info("import database: %s" % str(db_abs_path))
	data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, NAME_OLD_DATABASE_FILES, DATABASE_MODE)
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
											os.path.abspath(path_data_folder + NAME_LOG_FILE))
	# show correct usage
	logger_console.log_on_console_info("syntax : f-import FILENAME")
	logger_console.log_on_console_info("example: f-import fastHistory_2018-08-09.db")


def handle_export_db(logger_console, output_path, path_data_folder):
	"""
	export all database
	"""
	try:
		from shutil import copyfile
		from datetime import date
		
		if output_path is None:
			current_date = date.today()
			output_path = os.getcwd() + "/fastHistory_" + current_date.strftime("%Y-%m-%d") + ".db"

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
		copyfile(path_data_folder + NAME_DATABASE_FILE, output_path)
		logging.info("export output exported")
		logger_console.log_on_console_info("database file exported")
	except Exception as ex:
		logging.error("export database error: %s" % str(ex))
		logger_console.log_on_console_error("error: please check your log file: %s" %
											os.path.abspath(path_data_folder + NAME_LOG_FILE))
		logger_console.log_on_console_info("syntax : f-export [OUTPUT]")
		logger_console.log_on_console_info("example: f-export fastHistory_virtual_machine.db")


def edit_config_file(logger_console, path_data_folder):
	config_file= path_data_folder + NAME_CONFIGURATION_FILE
	logger_console.log_on_console_info("to change the config file use the following injected command")
	try:
		ConsoleUtils.fill_terminal_input("nano "+config_file)
	except:
		logger_console.log_on_console_error("your terminal does not support automatic input injection")
		logger_console.log_on_console_error("please edit the configuration file manually")
		logger_console.log_on_console(config_file)


def is_called_from_installer():
	"""
	check last input par to check if it is called by the installed
	"""
	if sys.argv[-1] == "--from-installer":
		del sys.argv[-1]
		return True
	else:
		return False


def retrieve_parameters_from_bash_hook(arg1=None):
	"""
	this variable is set by the bash hook (f.sh) and with this trick we can read also any comment as a parameter
	e.g. "f text #tag @desc" -> "text #tag @desc" (instead of only 'text')

	note: if 'f' is executed from a bash script, the hooked_cmd var will be the one from the script (e.g. "./script.sh par1"),
	therefore we must fall back to the normal behavior where the inline tags will not work
	"""
	if "_fast_history_hooked_cmd" in os.environ:
		var_len = len(os.environ["_fast_history_hooked_cmd"])
		var_value = os.environ["_fast_history_hooked_cmd"]
		if var_value == FAST_HISTORY_EXECUTABLE:
			return ""
		elif var_len > 1:
			if arg1:
				index = var_value.index(arg1)
				return str(var_value[index+len(arg1):]).strip()
			elif var_value[0:2] == FAST_HISTORY_EXECUTABLE + " ":
				return str(var_value[2:]).strip()
			else:
				logging.debug("$_fast_history_hooked_cmd belongs to other command: %s" % var_value)
				return " ".join(sys.argv[1:])
		else:
			logging.error("$_fast_history_hooked_cmd too short")
			return None
	else:
		logging.error("$_fast_history_hooked_cmd not found")
		return None


def f(logger_console=None):
	"""
	entry point
	"""
	if logger_console is None:
		logger_console = loggerBash.LoggerBash()
	ConsoleUtils.handle_close_signal()
	path_code_folder = os.path.dirname(os.path.realpath(__file__))
	path_data_folder = ConsoleUtils.compose_home_relative_path(PATH_DATA_FOLDER)
	is_from_installer = is_called_from_installer()

	# check for errors and load config file
	config_reader = ConfigReader(path_data_folder, path_code_folder,
								 skip_bash_checks=is_from_installer,
								 config_file=NAME_CONFIGURATION_FILE,
								 version_file=NAME_VERSION_FILE)
	if config_reader.check_config():
		logger_console.set_theme(config_reader.get_theme())

		# set logging (this setting is applied globally for all logging calls from now on)
		logging.basicConfig(filename=path_data_folder + NAME_LOG_FILE, level=config_reader.get_log_level())
		logging.debug("bash input: %s" % str(sys.argv))

		args_len = len(sys.argv)
		# check number of parameters
		if args_len == 1:
			input_cmd = retrieve_parameters_from_bash_hook()
			handle_search_request(logger_console, input_cmd, path_data_folder, config_reader.get_theme(), config_reader.get_last_column_size())
		elif args_len >= 2:
			arg1 = str(sys.argv[1])
			if arg1 == "-a" or arg1 == "--add":
				input_cmd = retrieve_parameters_from_bash_hook(arg1=arg1)
				handle_add_request(logger_console, input_cmd, path_data_folder, error_feedback=True)
			elif (arg1 == "--add-explicit") and args_len == 3:
				input_cmd = str(sys.argv[2]).strip()
				handle_add_request(logger_console, input_cmd, path_data_folder, error_feedback=False)
			elif (arg1 == "--config") and args_len == 2:
				edit_config_file(logger_console,path_data_folder)
			elif (arg1 == "--setup") and args_len == 2:
				from fastHistory.config.setupManager import SetupManager
				setup_manager = SetupManager(logger_console, path_data_folder, path_code_folder, NAME_CONFIGURATION_FILE, NAME_VERSION_FILE)
				setup_manager.auto_setup(force=True)
			elif arg1 == "--import" and args_len == 3:
				import_file = sys.argv[2]
				handle_import_db(logger_console, import_file, path_data_folder)
			elif arg1 == "--export" and args_len == 3:
				output_path = sys.argv[2]
				handle_export_db(logger_console, output_path, path_data_folder)
			elif arg1 == "--export" and args_len == 2:
				handle_export_db(logger_console, None, path_data_folder)
			elif (arg1 == "-h" or arg1 == "--help") and args_len == 2:
				from fastHistory.console.consoleHelp import HELP_STR
				logger_console.log_on_console(HELP_STR)
			elif (arg1 == "-v" or arg1 == "--version") and args_len == 2:
				logger_console.log_on_console(ConsoleUtils.open_file(path_data_folder + NAME_VERSION_FILE))
			else:
				input_cmd = retrieve_parameters_from_bash_hook()
				handle_search_request(logger_console, input_cmd, path_data_folder, config_reader.get_theme(), config_reader.get_last_column_size())
	elif len(sys.argv) >= 2 and (sys.argv[1] == "--config" or sys.argv[1] == "--setup"):
		if sys.argv[1] == "--config":
			edit_config_file(logger_console, path_data_folder)
		elif sys.argv[1] == "--setup":
			from fastHistory.config.setupManager import SetupManager
			setupManager = SetupManager(logger_console, path_data_folder, path_code_folder, NAME_CONFIGURATION_FILE, NAME_VERSION_FILE)
			setupManager.auto_setup(force=True)
		else:
			logger_console.log_on_console_error("corner case not handled")
	else:
		from fastHistory.config.setupManager import SetupManager
		setupManager = SetupManager(logger_console, path_data_folder, path_code_folder, NAME_CONFIGURATION_FILE, NAME_VERSION_FILE)
		setupManager.auto_setup(reason=config_reader.get_error_msg(), force=False)


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	print("the main of fastHistory is not enabled, please use the 'f()' function")
	
