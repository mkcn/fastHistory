from fastHistory.console import colors
from fastHistory.config.configReader import ConfigReader


class LoggerBash:

	tag_colored = None
	desc_colored = None
	log_fh_info = None
	log_fh_error = None
	log_debug = None
	log_info = None
	log_error = None

	def __init__(self):
		"""
		initialize colored variable with default theme (AZURE)
		"""
		self.tag_colored = colors.Cyan + "#" + colors.Color_Off
		self.desc_colored = colors.Cyan + "@" + colors.Color_Off
		self.log_fh_info = colors.Cyan + "fastHistory" + colors.Color_Off
		self.log_debug = colors.Cyan + "DEBUG" + colors.Color_Off

		self.log_error = colors.Red + "ERROR" + colors.Color_Off
		self.log_info = colors.White + "INFO " + colors.Color_Off
		self.log_fh_error = colors.Red + "fastHistory" + colors.Color_Off

	def set_theme(self, theme):
		"""
		change the color based on the configured theme

		:return:
		"""
		if theme == ConfigReader.THEME_GREEN:
			self.tag_colored = colors.Green + "#" + colors.Color_Off
			self.desc_colored = colors.Green + "@" + colors.Color_Off
			self.log_fh_info = colors.Green + "fastHistory" + colors.Color_Off
			self.log_debug = colors.Green + "DEBUG" + colors.Color_Off

	def log_on_console_info(self, msg):
		"""
		print an info message directly in the console
		the message will show the 'fastHistory' string color in blue
		:param msg:
		:return:
		"""
		print("[" + self.log_fh_info + "] " + str(msg))

	def log_on_console_error(self, msg):
		"""
		print an error message directly in the console
		the message will show the 'fastHistory' string color in red

		:param msg:
		:return:
		"""
		print("[" + self.log_fh_error + "] " + str(msg))

	def log_on_console(self, msg):
		"""
		print an message directly in the console

		:param msg:
		:return:
		"""
		print(str(msg))
