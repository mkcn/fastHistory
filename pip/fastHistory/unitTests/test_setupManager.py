import logging
import os
import shutil
from unittest import TestCase

from fastHistory.config.setupManager import SetupManager
from fastHistory.unitTests.loggerTest import LoggerTest, LoggerBashTest


class TestSetupManager(TestCase):

    STR_TEST = "test context"
    STR_HOOK = "source \"some_folder/fastHistory/bash/f.sh\""
    STR_HOOK_TO_IGNORE = "#source \"some_folder/fastHistory/bash/f.sh\""

    CONFIGURATION_FILE = "fastHistory.conf"
    VERSION_FILE = "version.txt"

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()

        cls.folder_home = cls.logger_test.get_test_folder() + "test_installation_home/"
        cls.folder_data = cls.logger_test.get_test_folder() + "test_installation_data/"
        cls.path_bashrc = cls.folder_home + ".bashrc"
        cls.path_zshrc = cls.folder_home + ".zshrc"
        cls.folder_code = os.path.dirname(os.path.realpath(__file__)) + "/.."

        cls.logger_console = LoggerBashTest()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())

        if os.path.exists(self.folder_data):
            shutil.rmtree(self.folder_data)
        if os.path.exists(self.folder_home):
            shutil.rmtree(self.folder_home)
        if not os.path.exists(self.folder_data):
            os.makedirs(self.folder_data)
        if not os.path.exists(self.folder_home):
            os.makedirs(self.folder_home)

    def _clean_and_setup_environment(self, bash=False, zsh=False):
        if bash:
            f = open(self.path_bashrc, "w")
            f.write(self.STR_TEST)
            f.close()
        if zsh:
            f = open(self.path_zshrc, "w")
            f.write(self.STR_TEST)
            f.close()

    def _check_correct_installation(self, hook_str=None, bash=None, zsh=None):
        res = os.path.isfile(self.folder_data + self.CONFIGURATION_FILE)
        self.assertTrue(res)
        res = os.path.isfile(self.folder_data + self.VERSION_FILE)
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
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.CONFIGURATION_FILE,
                             version_file=self.VERSION_FILE, home_path=self.folder_home)
        self.assertFalse(setup.handle_setup())
        res = os.path.isfile(self.folder_data + self.VERSION_FILE)
        self.assertFalse(res)

    def test_setup_with_basic_zsh_environment(self):
        self._clean_and_setup_environment(zsh=True)
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.CONFIGURATION_FILE,
                             version_file=self.VERSION_FILE, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), zsh=True)

    def test_setup_with_basic_bash_environment_and_fastHistory_already_installed(self):
        self._clean_and_setup_environment(bash=True)
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.CONFIGURATION_FILE,
                             version_file=self.VERSION_FILE, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)

        # simulate edit from user after fastHistory installation
        f = open(self.path_bashrc, "a")
        f.write("\n")
        f.write(self.STR_TEST)
        f.close()
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.CONFIGURATION_FILE,
                             version_file=self.VERSION_FILE, home_path=self.folder_home)
        self.assertTrue(setup.handle_setup())
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)
        with open(self.path_bashrc, 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            # if false, it means SetupManager has changed the file
            self.assertTrue(last_line == self.STR_TEST)
            f.close()

    def test_setup_with_bash_environment_with_old_hook(self):
        self._clean_and_setup_environment(bash=True)
        f = open(self.path_bashrc, "a")
        f.write("\n" + self.STR_HOOK)
        f.close()
        setup = SetupManager(self.logger_console, self.folder_data, self.folder_code, self.CONFIGURATION_FILE,
                             version_file=self.VERSION_FILE, home_path=self.folder_home)
        setup.handle_setup()
        self._check_correct_installation(hook_str=setup.get_hook_str(), bash=True)
        # the old hook should be removed by SetupManager
        f = open(self.path_bashrc, 'r')
        self.assertTrue(f.read().find(self.path_bashrc) == -1)
        f.close()





