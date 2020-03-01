import configparser
import os

class ConfigReader:
    """
    class used to read the configuration file
    """

    _MAIN = "GENERAL"
    _DB = "REMOTE DATABASE"
    _MAIN_LOG_LEVEL = "LOG_LEVEL"
    _MAIN_THEME = "THEME"
    _MAIN_TAGS_COLUMN_SIZE = "TAGS_COLUMN_SIZE"

    DB_ENABLED = "R_DB_ENABLED"
    DB_HOST = "R_DB_HOST"
    DB_PORT = "R_DB_PORT"
    DB_NAME = "R_DB_TABLE_NAME"
    DB_USER = "R_DB_USERNAME"
    DB_PASS = "R_DB_PASSWORD"
    ENC_PASS = "R_DB_ENC_PASSWORD"

    THEME_AZURE = "AZURE"
    THEME_GREEN = "GREEN"

    _ALLOWED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    _ALLOWED_THEME = [THEME_AZURE, THEME_GREEN]

    _config = None
    _checkError = ""

    def __init__(self, project_dir, config_file):
        
        self._config = configparser.ConfigParser()
        self.project_dir = project_dir
        self.config_path_file = project_dir + config_file

    def check_config(self):
        """
        validate configuration file

        :return: true if valid
        """
        if not os.path.isdir(self.project_dir):
            self._checkError = "project folder not found"
        else:
            self._config.read(self.config_path_file)
            if self._config is None:
                self._checkError = "file not found or malformed"
            elif self._MAIN not in self._config:
                self._checkError = "file not found or malformed"
            elif self._MAIN_LOG_LEVEL not in self._config[self._MAIN] or \
                self._config[self._MAIN][self._MAIN_LOG_LEVEL] not in self._ALLOWED_LOG_LEVELS:
                self._checkError = "%s must be chosen between: %s, current value: '%s'" % \
                        (self._MAIN_LOG_LEVEL,
                         str(self._ALLOWED_LOG_LEVELS),
                         self._config[self._MAIN][self._MAIN_LOG_LEVEL])
            elif self._MAIN_THEME not in self._config[self._MAIN] or \
                self._config[self._MAIN][self._MAIN_THEME] not in self._ALLOWED_THEME:
                self._checkError = "%s must be chosen between: %s, current value: '%s'" % \
                       (self._MAIN_THEME,
                        str(self._ALLOWED_THEME),
                        self._config[self._MAIN][self._MAIN_THEME])
            elif self._MAIN_TAGS_COLUMN_SIZE not in self._config[self._MAIN] or \
                 not self._config[self._MAIN][self._MAIN_TAGS_COLUMN_SIZE].isdigit():
                self._checkError = "%s must be a percentage between 0 and 50, current value: '%s'%%" % \
                        (self._MAIN_TAGS_COLUMN_SIZE,
                         self._config[self._MAIN][self._MAIN_TAGS_COLUMN_SIZE])
            else:
                 return True
        return False

    def get_error_msg(self):
        return self._checkError

    def get_log_level(self):
        return self._config[self._MAIN][self._MAIN_LOG_LEVEL]

    def get_theme(self):
        return self._config[self._MAIN][self._MAIN_THEME]

    def get_last_column_size(self):
        try:
            val = int(self._config[self._MAIN][self._MAIN_TAGS_COLUMN_SIZE])
            if val > 50:
                return 50
            else:
                return val
        except ValueError or Exception:
            return 0

    def get_config_database(self):
        return self._config[self._DB]



