import fcntl
import signal
import subprocess
import termios
import sys


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
		# put each char of data in the standard input of the current terminal
		for c in data:
			fcntl.ioctl(sys.stdin, termios.TIOCSTI, c)
		# clear output printed by the previous command
		# and leave only the terminal with the submitted input
		sys.stdout.write('\r')

	@staticmethod
	def handler_close_signal(signum, frame):
		"""
		gracefully close the program when a SIGINT (ctrl + c) is detected
		:param signum:
		:param frame:
		:return:
		"""
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