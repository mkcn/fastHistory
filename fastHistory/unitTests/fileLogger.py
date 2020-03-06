import logging


class FileLogger:

    def __init__(self, log_path):
        logging.basicConfig(filename=log_path, level=logging.DEBUG)

    def set_theme(self, theme):
        pass

    def log_on_console_info(self, msg):
        logging.info(str(msg))

    def log_on_console_warn(self, msg):
        logging.warning(str(msg))

    def log_on_console_error(self, msg):
        logging.error(str(msg))

    def log_on_console(self, msg):
        logging.info(str(msg))