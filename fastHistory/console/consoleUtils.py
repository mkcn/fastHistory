import fcntl
import signal
import subprocess
import termios
import sys


import struct
import os
from shutil import which


class ConsoleUtils:
	"""
	Useful methods to interact with the console
	"""

	@staticmethod
	def paste_into_terminal(data):
		"""
		Fill terminal input with data
		# https://unix.stackexchange.com/a/217390
		"""

		try:
			# check if python version >= 3
			if sys.version_info >= (3,):
				# reverse the automatic encoding and pack into a list of bytes
				data_bytes = (struct.pack('B', c) for c in os.fsencode(data))

			# put each char of data in the standard input of the current terminal
			for c in data_bytes:
				fcntl.ioctl(sys.stdin, termios.TIOCSTI, c)
			# clear output printed by the previous command
			# and leave only the terminal with the submitted input
			sys.stdout.write('\r')
			return [True, None]
		except Exception:
			res = ConsoleUtils.copy_to_clipboard(data)
			if res[0]:
				return [False, "your terminal does not support auto-paste, the command is copied to clipboard instead:\n%s" % data]
			else:
				return [False, "your terminal does not support auto-paste\ncopy-to-clipboard failed too with the following message:\n\t%s\nplease manually copy and use the following command:\n\t%s" % (res[1], data)]

	@staticmethod
	def copy_to_clipboard(data):
		try:
			import pyperclip
			pyperclip.copy(data)
			return [True, "copied to clipboard: %s" % data]
		except ImportError:
			return [False, "pyperclip module not found (to install it run 'pip3 install pyperclip')"]
		except Exception as e:
			return [False, "pyperclip error: %s" % str(e)]

	@staticmethod
	def is_cmd_available_on_this_machine(cmd_name):
		try:
			return which(cmd_name) is not None
		except:
			return False

	@staticmethod
	def handler_close_signal(signum, frame):
		"""
		gracefully close the program when a SIGINT (ctrl + c) is detected
		before to close it print a new line
		:param signum:
		:param frame:
		:return:
		"""
		print("")
		exit(0)

	@staticmethod
	def handle_close_signal():
		"""
		handle close signal
		:return:
		"""
		signal.signal(signal.SIGINT, ConsoleUtils.handler_close_signal)

	@staticmethod
	def open_interactive_man_page(cmd):
		"""
		open the real interactive man page

		:return:    return true if the man page has been open correctly
		"""
		if cmd is not None:
			res = subprocess.call(["man", cmd])
			if res == 0:
				return True
			else:
				return False
		return None

	@staticmethod
	def compose_home_relative_path(relative_path):
		if 'HOME' in os.environ:
			return os.environ['HOME'] + relative_path
		else:
			return None

	@staticmethod
	def open_file(file_path):
		try:
			f = open(file_path, "r")
			text = f.read().rstrip("\n")
		except IOError:
			text = "error reading file:" + file_path
		finally:
			f.close()
		return text
