import logging
import os
import inspect

from fastHistory.console.loggerBash import LoggerBash


class LoggerTest:

    TEST_FOLDER = "data_test/"
    TEST_LOG_FILENAME = "test_logs.txt"

    def __init__(self):
        self.test_folder_path = os.path.dirname(os.path.realpath(__file__)) + "/../../" + self.TEST_FOLDER

        if not os.path.exists(self.test_folder_path):
            os.makedirs(self.test_folder_path)

        log_path = self.test_folder_path + self.TEST_LOG_FILENAME
        logging.basicConfig(filename=log_path, level=logging.DEBUG)
        logging.info("@"*100)

    def get_test_folder(self):
        return self.test_folder_path

    def log_test_function_name(self, function_id):
        logging.info("#"*100)
        logging.info("##" + str(function_id))


class LoggerBashTest(LoggerBash):
    """
    class used to redirect the terminal output into the log file
    """

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