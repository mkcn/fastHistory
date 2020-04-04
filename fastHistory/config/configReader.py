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
    _BASH_SHARED_VALUE = "_fast_history_project_directory"

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
    _checkError = [False, ""]

    def __init__(self, project_dir, current_path, is_from_installer, config_file):
        
        self._config = configparser.ConfigParser()
        self.project_dir = project_dir
        self.current_path = current_path
        self.config_path_file = project_dir + config_file
        self.is_from_installer = is_from_installer

    def check_config(self):
        """
        check if:
            - configuration folder has been created, if not, probably is the first installation
            - the hook in the bash script is the correct one (detect bash issues, old installation, manual changes)
            - the configuration file has some invalid value

        :return: true if all checks are ok
        """
        general_advice = "Please use the '--config' option to fix it manually"

        if self.project_dir is None:
            self._checkError = [True, "$HOME variable cannot be found"]
        elif not os.path.isdir(self.project_dir):
            self._checkError = [True, "installation folder not found"]
        elif not self.is_from_installer and self._BASH_SHARED_VALUE not in os.environ:
            self._checkError = [False, "bash hook not set or loaded (you may have forgot to restart your terminal)"]
        elif not self.is_from_installer and os.environ[self._BASH_SHARED_VALUE] != self.current_path + "/bash/../":
            self._checkError = [True, "old bash hook found (reconfiguration needed)"]
        else:
            try:
                self._config.read(self.config_path_file)
                if self._config is None:
                    self._checkError = [False, "file not found or malformed"]
                elif self._MAIN not in self._config:
                    self._checkError = [False, "file not found or malformed"]
                elif self._MAIN_LOG_LEVEL not in self._config[self._MAIN] or \
                    self._config[self._MAIN][self._MAIN_LOG_LEVEL] not in self._ALLOWED_LOG_LEVELS:
                    self._checkError = [None, "%s must be chosen between: %s, current value: '%s'. %s" % \
                            (self._MAIN_LOG_LEVEL,
                             str(self._ALLOWED_LOG_LEVELS),
                             self._config[self._MAIN][self._MAIN_LOG_LEVEL],
                             general_advice)]
                elif self._MAIN_THEME not in self._config[self._MAIN] or \
                    self._config[self._MAIN][self._MAIN_THEME] not in self._ALLOWED_THEME:
                    self._checkError = [None, "%s must be chosen between: %s, current value: '%s'. %s" % \
                           (self._MAIN_THEME,
                            str(self._ALLOWED_THEME),
                            self._config[self._MAIN][self._MAIN_THEME],
                            general_advice)]
                elif self._MAIN_TAGS_COLUMN_SIZE not in self._config[self._MAIN] or \
                     not self._config[self._MAIN][self._MAIN_TAGS_COLUMN_SIZE].isdigit():
                    self._checkError = [None, "%s must be a percentage between 0 and 50, current value: '%s'%%. %s" % \
                            (self._MAIN_TAGS_COLUMN_SIZE,
                             self._config[self._MAIN][self._MAIN_TAGS_COLUMN_SIZE],
                             general_advice)]
                else:
                     return True
            except KeyError as err:
                self._checkError = [None, "error in configuration file with key: " + str(err) + ". " + general_advice]

            except:
                self._checkError = [None, "generic error with configuration file. " + general_advice]
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



