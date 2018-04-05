import unittest
import logging
import os
import inspect
from database.databaseSQLite import DatabaseSQLite


class TestDatabaseSQLite(unittest.TestCase):

    log_file_name = "data/test_databaseSQLite.log"

    def setUp(self):
        current_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
        self.db_path = current_path
        self.log_path = current_path + self.log_file_name

        logging.basicConfig(filename=self.log_path, level=logging.DEBUG)

    def test_get_all_data(self):
        self._set_text_logger()

        db = DatabaseSQLite(self.db_path)

        for i in db.get_all_data():
            logging.info(str(i))
        db.close()

    def test_get_first_50_elements(self):
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path)
        word = "secs"
        logging.info("search for: " + word)
        for i in db.get_last_N_elements(n=50):
            logging.info(str(i))
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
            db.add_element("ls " + str(i), "test " + str(i), ["sec" + str(i)])
        db.save_changes()

        res = db.get_last_N_elements(n=tot_line*10)
        self.assertEqual(len(res), tot_line)

        db.close()

    def test_fill_db_with_same_entry(self):
        """"
        store same command multiple times with different description and tags
        try then to retrieve it
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.db_path, delete_old_db=True)
        db.add_element("ls -ls", "test1", ["security"])
        db.add_element("ls -ls", "test2", None)
        db.add_element("ls -ls", "test3", ["sec", "security", "supersecure"])

        res = db.get_last_N_elements(filter="supersecure")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][2], "#security#sec#supersecure")
        db.close()

    def _set_text_logger(self):
        """
        set global setting of the logging class and print (dynamically) the name of the running test
        :return:
        """
        logging.info("*" * 30)
        # 0 is the current function, 1 is the caller
        logging.info("Start test '" + str(inspect.stack()[1][3]) + "'")
