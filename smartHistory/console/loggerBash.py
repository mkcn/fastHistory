from console import colors

LOG_ERROR = colors.Red + "ERROR" + colors.Color_Off
LOG_INFO = colors.White + "INFO " + colors.Color_Off
LOG_DEBUG = colors.Blue + "DEBUG" + colors.Color_Off
LOG_SH_INFO = colors.Blue + "Smart History" + colors.Color_Off
LOG_SH_ERROR = colors.Red + "Smart History" + colors.Color_Off


def log_on_console_info(msg):
	print("[" + LOG_SH_INFO + "] " + str(msg))


def log_on_console_error(msg):
	print("[" + LOG_SH_ERROR + "] " + str(msg))
