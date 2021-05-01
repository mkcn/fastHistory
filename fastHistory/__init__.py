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

DATABASE_MODE = DataManager.DATABASE_MODE_SQLITE


def handle_search_request(logger_console, input_cmd_str, path_data_folder, theme, last_column_size, is_tldr_search=False):
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
		data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, DATABASE_MODE)

		# open picker to select from history
		picker = Picker(data_manager,
						theme=theme,
						last_column_size=last_column_size,
						search_text=input_cmd_str,
						is_tldr_search=is_tldr_search)
		selected_option = picker.start()

		if selected_option[0]:
			res = ConsoleUtils.paste_into_terminal(selected_option[1])
			if not res[0]:
				logger_console.log_on_console_error(res[1])
		else:
			res = ConsoleUtils.copy_to_clipboard(selected_option[1])
			if res[0]:
				logger_console.log_on_console_info(res[1])
			else:
				logger_console.log_on_console_error(res[1])


def handle_add_request(logger_console, input_cmd_str, path_data_folder, error_feedback=False):
	"""
	take input and add store it

	:return:
	"""
	# local import to load this module only in case of an 'add' commands
	from fastHistory.parser.inputParser import InputParser

	input = InputParser.adjust_multi_line_input(input_cmd_str)

	# define log class
	logging.debug("add request: '" + input[1] + "'")

	# parse tags and store the cmd
	parser_res = InputParser.parse_input(input[1])

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

		data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, DATABASE_MODE)
		stored = data_manager.add_new_element(cmd, description, tags)
		if stored:
			logging.debug("command added")
			if input[0]:
				logger_console.log_on_console_warn("command has been adjusted")
				logger_console.log_on_console_warn("multi-line commands are not fully supported")
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
	data_manager = DataManager(path_data_folder, NAME_DATABASE_FILE, DATABASE_MODE)
	imported_items = data_manager.import_data_to_db(db_abs_path)
	if imported_items >= 0:
		logging.info("import database: %s elements imported" % str(imported_items))
		logger_console.log_on_console_info("import database: %s elements imported" % str(imported_items))
		return
	elif not os.path.isfile(db_abs_path):
		logging.error("input file does not exist: %s" % str(db_abs_path))
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

		logging.info("output: %s " % str(output_path))
		logger_console.log_on_console_info("export output: %s " % str(output_path))
		if os.path.isfile(output_path):
			answer = input("output file already exits, overwrite it? [y/N] ")
			if answer.lower() != "y":
				logger_console.log_on_console_error("export database cancel")
				return
		if os.path.isdir(output_path):
			logger_console.log_on_console_error("output path cannot be a directory")
			return
		if not os.path.isfile(path_data_folder + NAME_DATABASE_FILE):
			logger_console.log_on_console_info("nothing to export")
			return
		copyfile(path_data_folder + NAME_DATABASE_FILE, output_path)
		logging.info("export output exported")
		logger_console.log_on_console_info("database file exported")
	except Exception as ex:
		logging.error("export database error: %s" % str(ex))
		logger_console.log_on_console_error("export failed, please check your log file: %s" %
											os.path.abspath(path_data_folder + NAME_LOG_FILE))
		logger_console.log_on_console_info("syntax : f-export [OUTPUT]")
		logger_console.log_on_console_info("example: f-export fastHistory_virtual_machine.db")


def handle_setup(logger_console, path_data_folder, path_code_folder, config_reader, reason=None, force=False):
	from fastHistory.config.setupManager import SetupManager
	setup_manager = SetupManager(logger_console, path_data_folder, path_code_folder, NAME_CONFIGURATION_FILE, NAME_VERSION_FILE)
	if setup_manager.auto_setup(reason=reason, force=force):
		if config_reader.check_config():
			return True
		else:
			logger_console.log_on_console_warn("please restart your terminal and then use 'f' to start")
			return False
	else:
		return False


def handle_update(logger_console):
	update_command = "pip3 install -U --no-cache-dir --user fastHistory && $HOME/.local/bin/f"
	update_with_installer = "cd $(mktemp -d /tmp/f.XXXXX) && wget mkcn.me/f && tar -xvzf f && ./fastHistory-*/installer.sh && cd -"
	try:
		from importlib import util
		if util.find_spec("pip") is None:
			update_command = update_with_installer
	except ImportError as e:
		update_command = update_with_installer
	logger_console.log_on_console_info("to update fastHistory use the following command")
	res = ConsoleUtils.paste_into_terminal(update_command)
	if not res[0]:
		logger_console.log_on_console_error(res[1])


def handle_config_file(logger_console, path_data_folder):
	config_file = path_data_folder + NAME_CONFIGURATION_FILE
	logger_console.log_on_console_info("to change the config file use the following command")
	res = ConsoleUtils.paste_into_terminal("nano " + config_file)
	if not res[0]:
		logger_console.log_on_console_error(res[1])


def handle_log_file(logger_console, path_data_folder):
	log_file = path_data_folder + NAME_LOG_FILE
	if not os.path.exists(log_file):
		logger_console.log_on_console_warn("log file not found, try to change the log level in the config file")
	else:
		logger_console.log_on_console_info("to read the log file use the following command")
		res = ConsoleUtils.paste_into_terminal("nano " + log_file)
		if not res[0]:
			logger_console.log_on_console_error(res[1])


def handle_helper(logger_console):
	from fastHistory.console.consoleHelp import HELP_STR
	logger_console.log_on_console(HELP_STR)


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
			if arg1 is not None:
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


def handle_arguments(logger_console, config_reader, path_data_folder, path_code_folder):
	# set logging (this setting is applied globally for all logging calls from now on)
	if config_reader.get_log_level() == 'NOTSET' or config_reader.get_log_level() == 'NONE':
		logging.disable(logging.CRITICAL)
	else:
		logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
			datefmt='%Y-%m-%d %H:%M:%S',
			filename=path_data_folder + NAME_LOG_FILE,
			level=config_reader.get_log_level())
	logging.debug("bash input: %s" % str(sys.argv))
	logger_console.set_theme(config_reader.get_theme())
	args_len = len(sys.argv)
	# check number of parameters
	if args_len == 1:
		input_cmd = retrieve_parameters_from_bash_hook()
		handle_search_request(logger_console, input_cmd, path_data_folder, config_reader.get_theme(),
							  config_reader.get_last_column_size())
	elif args_len >= 2:
		arg1 = str(sys.argv[1])
		if arg1 == "-a" or arg1 == "--add":
			input_cmd = retrieve_parameters_from_bash_hook(arg1=arg1)
			handle_add_request(logger_console, input_cmd, path_data_folder, error_feedback=True)
		elif arg1 == "--add-explicit" and args_len == 3:
			input_cmd = str(sys.argv[2]).strip()
			handle_add_request(logger_console, input_cmd, path_data_folder, error_feedback=False)
		elif arg1 == "-f" or arg1 == "--find" or arg1 == "--tldr":
			input_cmd = retrieve_parameters_from_bash_hook(arg1=arg1)
			handle_search_request(logger_console, input_cmd, path_data_folder, config_reader.get_theme(),
								  config_reader.get_last_column_size(), is_tldr_search=True)
		elif arg1 == "--config" and args_len == 2:
			handle_config_file(logger_console, path_data_folder)
		elif arg1 == "--log" and args_len == 2:
			handle_log_file(logger_console, path_data_folder)
		elif arg1 == "--setup" and args_len == 2:
			handle_setup(logger_console, path_data_folder, path_code_folder, config_reader, force=True)
		elif arg1 == "--import" and args_len == 3:
			import_file = sys.argv[2]
			handle_import_db(logger_console, import_file, path_data_folder)
		elif arg1 == "--export" and args_len == 3:
			output_path = sys.argv[2]
			handle_export_db(logger_console, output_path, path_data_folder)
		elif arg1 == "--export" and args_len == 2:
			handle_export_db(logger_console, None, path_data_folder)
		elif arg1 == "--update" and args_len == 2:
			handle_update(logger_console)
		elif (arg1 == "-h" or arg1 == "--help") and args_len == 2:
			handle_helper(logger_console)
		elif (arg1 == "-v" or arg1 == "--version") and args_len == 2:
			logger_console.log_on_console(ConsoleUtils.open_file(path_data_folder + NAME_VERSION_FILE))
		else:
			input_cmd = retrieve_parameters_from_bash_hook()
			handle_search_request(logger_console, input_cmd, path_data_folder, config_reader.get_theme(),
								config_reader.get_last_column_size())
	else:
		logger_console.log_on_console_error("wrong number of args")


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
		handle_arguments(logger_console, config_reader, path_data_folder, path_code_folder)
	elif len(sys.argv) >= 2 and (sys.argv[1] in ["--config", "-h", "--help", "--setup"]):
		if sys.argv[1] == "--config":
			handle_config_file(logger_console, path_data_folder)
		elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
			handle_helper(logger_console)
		elif sys.argv[1] == "--setup":
			handle_setup(logger_console, path_data_folder, path_code_folder, config_reader, force=True)
	else:
		if handle_setup(logger_console, path_data_folder, path_code_folder, config_reader, reason=config_reader.get_error_msg()):
			handle_arguments(logger_console, config_reader, path_data_folder, path_code_folder)


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	print("the main of fastHistory is not enabled, please use the 'f()' function")

