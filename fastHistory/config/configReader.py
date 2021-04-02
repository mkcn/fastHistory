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
    _BASH_VAR_VERSION = "_fast_history_version"
    _BASH_VAR_PATH_CODE_FOLDER = "_fast_history_path_code_folder"

    DB_ENABLED = "R_DB_ENABLED"
    DB_HOST = "R_DB_HOST"
    DB_PORT = "R_DB_PORT"
    DB_NAME = "R_DB_TABLE_NAME"
    DB_USER = "R_DB_USERNAME"
    DB_PASS = "R_DB_PASSWORD"
    ENC_PASS = "R_DB_ENC_PASSWORD"

    THEME_AZURE = "AZURE"
    THEME_GREEN = "GREEN"

    # NOTSET may be used by old configutation files ( <= 2.1.5) and it must be considered equal to NONE
    _ALLOWED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET', 'NONE']
    _ALLOWED_THEME = [THEME_AZURE, THEME_GREEN]

    _config = None
    _checkError = [False, ""]

    def __init__(self, path_data_folder, path_code_folder, skip_bash_checks, config_file, version_file):
        
        self._config = configparser.ConfigParser()
        self.path_data_folder = path_data_folder
        self.path_code_folder = path_code_folder
        self.path_config_file = path_data_folder + config_file
        self.path_data_version_file = path_data_folder + version_file
        self.path_code_version_file = path_code_folder + "/config/default_" + version_file
        self.skip_bash_checks = skip_bash_checks

    def check_config(self):
        """
        check if:
            - configuration folder has been created, if not, probably is the first installation
            - the hook in the bash script is the correct one (detect bash issues, old installation, manual changes)
            - the configuration file has some invalid value

        in case of issues it fills the _checkError variable with array:
                        [ True = possible correct flow of fastHistory |
                        False = issue which can be fixed automatically |
                        None = issue which need to be fixed manually
                        ,
                        message string to show]

        :return: true if all checks are ok
        """
        general_advice = "Please use the '--config' option to fix it manually"

        if self.path_data_folder is None:
            # TODO check $HOME and fix
            self._checkError = [None, "$HOME variable cannot be found"]
        elif not os.path.isdir(self.path_data_folder):
            self._checkError = [True, "installation folder not found"]
        else:
            data_version = self._get_content_version_file(self.path_data_version_file)
            code_version = self._get_content_version_file(self.path_code_version_file)
            if data_version is None:
                self._checkError = [False, "data version file cannot be read"]
            elif data_version != code_version:
                self._checkError = [True, "update detected, data folder needs to be updated (%s -> %s)" %
                                    (data_version, code_version)]
            elif not self.skip_bash_checks and (
                    self._BASH_VAR_PATH_CODE_FOLDER not in os.environ or self._BASH_VAR_VERSION not in os.environ):
                self._checkError = [False, "bash hook not loaded (you may forgot to restart your terminal)"]
            elif not self.skip_bash_checks and os.environ[self._BASH_VAR_PATH_CODE_FOLDER] != self.path_code_folder + "/bash/../":
                self._checkError = [False, "wrong bash hook loaded (maybe from an old installation)"]
            elif not self.skip_bash_checks and str(os.environ[self._BASH_VAR_VERSION]) != code_version:
                self._checkError = [None, "restart your terminal, old bash is still used (%s -> %s)" %
                                    (os.environ[self._BASH_VAR_VERSION], code_version)]
            else:
                try:
                    self._config.read(self.path_config_file)
                    if self._config is None:
                        self._checkError = [False, "config file not found"]
                    elif self._MAIN not in self._config:
                        self._checkError = [None, "config file malformed"]
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
                    self._checkError = [None, "error in config file with key: " + str(err) + ". " + general_advice]
                except:
                    self._checkError = [None, "generic error with config file. " + general_advice]
        return False

    def _get_content_version_file(self, path):
        try:
            f = open(path, "r")
            content = f.read().rstrip()
            f.close()
            return content
        except:
            return None

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



