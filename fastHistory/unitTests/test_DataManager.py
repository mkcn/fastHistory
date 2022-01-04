import os
import unittest

from fastHistory import DataManager
from fastHistory.database.databaseSQLite import DatabaseSQLite
from fastHistory.unitTests.loggerTest import LoggerTest


class TestDataManager(unittest.TestCase):

    TEST_DB_FILENAME = "test_databaseSQLiteDataManager.db"

    @classmethod
    def setUpClass(cls):
        cls.logger_test = LoggerTest()
        cls.output_test_path = cls.logger_test.get_test_folder()

    def setUp(self):
        self.logger_test.log_test_function_name(self.id())
        if os.path.exists(self.output_test_path + self.TEST_DB_FILENAME):
            os.remove(self.output_test_path + self.TEST_DB_FILENAME)

    def test_add_update_filter_delete_flow(self):
        data_manager = DataManager(self.output_test_path, self.TEST_DB_FILENAME)
        self.assertTrue(data_manager.add_new_element("cmd1", "desc1", ["tag1"]))
        self.assertTrue(data_manager.update_command("cmd1", "cmd2"))
        self.assertTrue(data_manager.update_description("cmd2", "desc2"))
        self.assertTrue(data_manager.update_tags("cmd2", ["tag2"]))
        self.assertEqual(len(data_manager.get_data_from_db()), 1)
        self.assertEqual(data_manager.get_search_filters().get_description_str(), None)
        self.assertEqual(len(data_manager.filter("cmd1")), 0)
        self.assertEqual(len(data_manager.filter("cmd2")), 1)
        self.assertEqual(len(data_manager.filter("CMD2")), 1)
        self.assertEqual(len(data_manager.filter(" CMD2   ")), 1)
        self.assertEqual(len(data_manager.filter("#tag2")), 1)
        self.assertEqual(len(data_manager.filter("@desc2")), 1)
        self.assertEqual(len(data_manager.filter("@desc2 #tag-after-desc")), 0)
        self.assertEqual(len(data_manager.filter("cmd2 #tag2")), 1)
        self.assertEqual(len(data_manager.filter("cmd2 #tag2 @desc2")), 1)
        self.assertEqual(data_manager.get_search_filters().get_description_str(), "desc2")
        self.assertTrue(data_manager.delete_element("cmd2"))
        self.assertEqual(len(data_manager.get_data_from_db()), 0)

    def test_update_element_order(self):
        data_manager = DataManager(self.output_test_path, self.TEST_DB_FILENAME)
        self.assertTrue(data_manager.add_new_element("cmd1", "desc1", ["tag1"]))
        self.assertTrue(data_manager.add_new_element("cmd2", "desc2", ["tag2"]))
        self.assertTrue(data_manager.add_new_element("cmd3", "desc3", ["tag3"]))
        self.assertTrue(data_manager.update_selected_element_order("cmd1"))
        self.assertEqual(data_manager.get_data_from_db()[-1][DatabaseSQLite.COLUMN_INDEX_COMMAND], "cmd1")

    def test_get_forbidden_chars(self):
        data_manager = DataManager(self.output_test_path, self.TEST_DB_FILENAME)
        self.assertEqual(len(data_manager.get_forbidden_chars()), 3)
