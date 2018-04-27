from console import colors

LOG_ERROR = colors.Red + "ERROR" + colors.Color_Off
LOG_INFO = colors.White + "INFO " + colors.Color_Off
LOG_DEBUG = colors.Blue + "DEBUG" + colors.Color_Off
LOG_SH_INFO = colors.Blue + "fastHistory" + colors.Color_Off
LOG_SH_ERROR = colors.Red + "fastHistory" + colors.Color_Off


def log_on_console_info(msg):
	"""
	print an info message directly in the console
	the message will show the 'fastHistory' string color in blue
	:param msg:
	:return:
	"""
	print("[" + LOG_SH_INFO + "] " + str(msg))


def log_on_console_error(msg):
	"""
	print an error message directly in the console
	the message will show the 'fastHistory' string color in red

	:param msg:
	:return:
	"""
	print("[" + LOG_SH_ERROR + "] " + str(msg))


def log_on_console(msg):
	"""
	print an message directly in the console

	:param msg:
	:return:
	"""
	print(str(msg))
