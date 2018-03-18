#!/usr/bin/python

import sys
import os
import logging


LOG_FILE_NAME = "logs/smartHistory.log"


def handle_search_request(input_cmd_str):
	"""
	take input and show the filtered list of command to select
	:param input_cmd_str:	input cmd
	:return:
	"""
	# local import to not affect the response time of the bash command
	from console.consoleUtils import ConsoleUtils
	from pick.picker import pick

	logging.info("search request: '" + input_cmd_str + "'")
	# set SIGINT handler
	ConsoleUtils.handle_close_signal()
	# open picker to select from history
	selected_option, index = pick(search_text=input_cmd_str)
	selected_string = selected_option[0]
	# show selected cmd
	ConsoleUtils.fill_terminal_input(selected_string)


def handle_add_request(input_cmd_str, feedback=False):
	"""
	take input and add store it
	:param input_cmd_str:	input cmd
	:param feedback:		if true prints feedback message in the console, otherwise hides all
	:return:
	"""
	# local import to not affect the response time of the bash command
	from parser import tagParser
	from collector.saver import Saver
	from console.loggerBash import log_on_console_info, log_on_console_error

	# define log class
	logging.info("add request: '" + input_cmd_str + "'")

	# if no privacy mode add the command
	if not tagParser.TagParser.is_privacy_mode_enable(input_cmd):
		# parse tags and store the cmd
		parser_res = tagParser.TagParser.parse_cmd(input_cmd_str)
		# log_info(parser_res)
		x = Saver(input_text=parser_res)
		if feedback:
			log_on_console_info("command: added")
	else:
		if feedback:
			log_on_console_info("PRIVACY mode ENABLED")


if __name__ == "__main__":
	"""
	main function called by the precmd hook bash command
	"""
	# check number of parameters
	if len(sys.argv) == 3:

		doc_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		logging.basicConfig(filename=doc_path + LOG_FILE_NAME, level=logging.DEBUG)
		logging.debug("bash input: " + str(sys.argv))

		mode = str(sys.argv[1])
		input_cmd = str(sys.argv[2])
		if mode == "search":
			handle_search_request(input_cmd)
		elif mode == "add":
			handle_add_request(input_cmd, True)
		elif mode == "add-silent" and len(input_cmd) > 0:
			handle_add_request(input_cmd)
	else:
		# TODO print usage
		pass

