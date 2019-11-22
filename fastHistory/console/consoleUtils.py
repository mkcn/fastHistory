import fcntl
import signal
import subprocess
import termios
import sys

import struct
import os


class ConsoleUtils:
	"""
	Useful methods to interact with the console
	"""

	@staticmethod
	def fill_terminal_input(data):
		"""
		Fill terminal input with data
		# https://unix.stackexchange.com/a/217390
		"""
		# check if python version >= 3
		if sys.version_info >= (3,):
			# reverse the automatic encoding and pack into a list of bytes
			data = (struct.pack('B', c) for c in os.fsencode(data))

		# put each char of data in the standard input of the current terminal
		for c in data:
			fcntl.ioctl(sys.stdin, termios.TIOCSTI, c)
		# clear output printed by the previous command
		# and leave only the terminal with the submitted input
		sys.stdout.write('\r')

	@staticmethod
	def set_value_clipboard(data):
		try:
			import pyperclip
			pyperclip.copy(data)
			return True
		except Exception as e:
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
			try:
				res = subprocess.call(["man", cmd])
				return res == 0
			except Exception as e:
				return False
		return False
