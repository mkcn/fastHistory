import unittest
import logging
import os
import inspect
from database.databaseSQLite import DatabaseSQLite


class TestDatabaseSQLite(unittest.TestCase):

    TEST_LOG_FILENAME = "data/test_databaseSQLite.log"
    TEST_DB_FILENAME = "data/test_databaseSQLite.db"

    def setUp(self):
        """
        initial set for logging and current path

        :return:
        """
        current_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
        self.db_path = current_path + self.TEST_DB_FILENAME
        self.log_path = current_path + self.TEST_LOG_FILENAME

        logging.basicConfig(filename=self.log_path, level=logging.DEBUG)

    def test_get_first_20_filtered_elements(self):
        """
        fill db with 25 element (ls command) and retrieve the first 20 ls commands

        :return:
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        for i in range(25):
            self.assertTrue(db.add_element("ls " + str(i), "test " + str(i), ["sec" + str(i)]))

        res = db.get_last_n_elements_with_advanced_search(cmd_filter="ls",
                                                          tags_filter="",
                                                          description_filter="",
                                                          n=20)
        self.assertEqual(len(res), 20)

        db.close()

    def test_fill_db_with_100_entries(self):
        """
        fill db with 100 different entries and then check if db contain 100 entries
        :return:
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        tot_line = 100
        for i in range(tot_line):
            self.assertTrue(db.add_element("ls " + str(i), "test " + str(i), ["sec" + str(i)]))
        db.save_changes()
        # try to retrieve 200 entries
        res = db.get_last_n_elements_with_simple_search(n=tot_line*2)
        self.assertEqual(len(res), tot_line)

        db.close()

    def test_fill_db_with_same_entries(self):
        """"
        store same command multiple times with different description and tags
        try then to retrieve it
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        self.assertTrue(db.add_element("ls -ls", "test1", ["security"]))
        self.assertTrue(db.add_element("ls -ls", "test2", None))
        self.assertTrue(db.add_element("ls -ls", "test3", ["sec", "security", "supersecure"]))

        res = db.get_last_n_elements_with_simple_search(filter="supersecure")
        # check number of matches
        self.assertEqual(len(res), 1)
        # check if tags are saved correctly
        self.assertEqual(res[0][2], "#security#sec#supersecure")
        # check if description is updated
        self.assertEqual(res[0][1], "test3")
        db.close()

    def test_fill_db_with_wrong_entries(self):
        """"
        store same command multiple times with different description and tags
        try then to retrieve it
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        # illegal @ char
        self.assertFalse(db.add_element("test 1", "@test", ["test"]))
        self.assertFalse(db.add_element("test 2", "@test", ["@test"]))
        # illegal # char
        self.assertFalse(db.add_element("test 3", "#test", ["test"]))
        self.assertFalse(db.add_element("test 4", "test", ["#test"]))

        db.close()

    def test_get_all_data(self):
        """
        this is used only for manual debug purposes

        :return:
        """
        self._set_text_logger()

        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        db.add_element("ls", "test", ["sec"])
        db.add_element("ls", "test 2", ["sec"])

        for i in db.get_all_data():
            logging.info(str(i))
        db.close()

    def _set_text_logger(self):
        """
        set global setting of the logging class and print (dynamically) the name of the running test
        :return:
        """
        logging.info("*" * 30)
        # 0 is the current function, 1 is the caller
        logging.info("Start test '" + str(inspect.stack()[1][3]) + "'")
