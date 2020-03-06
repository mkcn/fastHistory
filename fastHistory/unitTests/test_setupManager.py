import logging
import os
import shutil
from unittest import TestCase

from fastHistory.config.setupManager import SetupManager
from fastHistory.unitTests.fileLogger import FileLogger
import inspect


class TestSetupManager(TestCase):

    TEST_FOLDER = "/data_test/"
    TEST_LOG_FILENAME = "test_setupManager.txt"

    def setUp(self):
        """
        setup absolute log path and log level
        :return:
        """
        # TODO create shared test class for setup
        self.folder_code = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.folder_test_output = os.path.dirname(self.folder_code) + self.TEST_FOLDER
        self.folder_home = self.folder_test_output + "test_installation_home/"
        self.folder_data = self.folder_test_output + "test_installation_data/"

        self.path_bashrc = self.folder_home + ".bashrc"
        self.path_zshrc = self.folder_home + ".zshrc"


        self.context_test = "test context"
        self.context_hook = "source \"some_folder/fastHistory/bash/f.sh\""
        self.context_hook_to_ignore = "#source \"some_folder/fastHistory/bash/f.sh\""

        self.log_path = self.folder_test_output + self.TEST_LOG_FILENAME
        self.configuration_file = "fastHistory.conf"
        self.version_file = "version.txt"

        self.logger_console = FileLogger(self.log_path)
        logging.basicConfig(filename=self.log_path, level=logging.DEBUG)

    def _clean_and_setup_environment(self, bash=False, zsh=False):
        if os.path.exists(self.folder_data):
            shutil.rmtree(self.folder_data)
        if os.path.exists(self.folder_home):
            shutil.rmtree(self.folder_home)
        if not os.path.exists(self.folder_test_output):
            os.makedirs(self.folder_test_output)
        if not os.path.exists(self.folder_data):
            os.makedirs(self.folder_data)
        if not os.path.exists(self.folder_home):
            os.makedirs(self.folder_home)
        if bash:
            f = open(self.path_bashrc , "w")
            f.write(self.context_test)
            f.close()
        if zsh:
            f = open(self.path_zshrc , "w")
            f.write(self.context_test)
            f.close()

    def _check_correct_installation(self, hook_str=None, bash=None, zsh=None):
        res = os.path.isfile(self.folder_data + self.configuration_file)
        self.assertTrue(res)
        res = os.path.isfile(self.folder_data + self.version_file)
        self.assertTrue(res)
        # note: in our check we add "\n" to check if the line start with the "hook_str" string
        # this is done to do a different check that the one already in the SetupManager class
        if bash:
            f = open(self.path_bashrc, 'r')
            self.assertTrue(f.read().find("\n" + hook_str) != -1)
            f.close()
        if zsh:
            f = open(self.path_zshrc, 'r')
            self.assertTrue(f.read().find("\n" + hook_str) != -1)
            f.close()

    def test_setup_fail_with_empty_environment(self):
        self._set_text_logger()
        self._clean_and_setup_environment()
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.configuration_file, version_file=self.version_file, home_path=self.folder_home)
        self.assertFalse(setup.handle_setup())
        res = os.path.isfile(self.folder_data + self.version_file)
        self.assertFalse(res)

    def test_setup_with_basic_zsh_environment(self):
        self._set_text_logger()
        self._clean_and_setup_environment(zsh=True)
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.configuration_file, version_file=self.version_file, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), zsh=True)

    def test_setup_with_basic_bash_environment(self):
        self._set_text_logger()
        self._clean_and_setup_environment(bash=True)
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.configuration_file, version_file=self.version_file, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)

    # NOTE: this is executed after test_setup_with_basic_bash_environment (execution order based on function name)
    def test_setup_with_basic_bash_environment_and_fastHistory_already_installed(self):
        self._set_text_logger()
        self._check_correct_installation()
        # simulate edit from user after fastHistory installation
        f = open(self.path_bashrc, "a")
        f.write("\n")
        f.write(self.context_test)
        f.close()
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.configuration_file,
                             version_file=self.version_file, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)
        with open(self.path_bashrc, 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            # if false, it means SetupManager has changed the file
            self.assertTrue(last_line == self.context_test)
            f.close()

    def test_setup_with_bash_environment_with_old_hook(self):
        self._set_text_logger()
        self._clean_and_setup_environment(bash=True)
        f = open(self.path_bashrc, "a")
        f.write("\n" + self.context_hook)
        f.close()
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.configuration_file, version_file=self.version_file, home_path=self.folder_home)
        setup.handle_setup()
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)
        # the old hook should be removed by SetupManager
        f = open(self.path_bashrc, 'r')
        self.assertTrue(f.read().find(self.path_bashrc) == -1)
        f.close()

    def test_backup_rc_creation(self):
        #TODO
        pass 

    def _set_text_logger(self):
        """
        set global setting of the logging class and print (dynamically) the name of the running test
        :return:
        """
        logging.info("*" * 30)
        # 0 is the current function, 1 is the caller
        logging.info("Start test '" + str(inspect.stack()[1][3]) + "'")



