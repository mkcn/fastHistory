import unittest
import logging
import os
import inspect
from database.databaseSQLite import DatabaseSQLite
import sqlite3


class TestDatabaseSQLite(unittest.TestCase):

    TEST_FOLDER = "../../data_test/"
    TEST_LOG_FILENAME = "test_databaseSQLite.log"
    TEST_DB_FILENAME = "test_databaseSQLite.db"
    TEST_DB_FILENAME_OLD = "test_databaseSQLite_old.db"

    def setUp(self):
        """
        initial set for logging and current path

        :return:
        """
        self.output_test_path = os.path.dirname(os.path.realpath(__file__)) + "/" + self.TEST_FOLDER
        if not os.path.exists(self.output_test_path):
            os.makedirs(self.output_test_path)
        self.db_path = self.output_test_path + self.TEST_DB_FILENAME
        self.log_path = self.output_test_path + self.TEST_LOG_FILENAME

        logging.basicConfig(filename=self.log_path, level=logging.DEBUG)

    def test_get_first_20_filtered_elements(self):
        """
        fill db with 25 element (ls command) and retrieve the first 20 ls commands

        :return:
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.output_test_path, self.TEST_DB_FILENAME, None, delete_all_data_from_db=True)
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
        db = DatabaseSQLite(self.output_test_path, self.TEST_DB_FILENAME, None, delete_all_data_from_db=True)
        tot_line = 100
        for i in range(tot_line):
            self.assertTrue(db.add_element("ls " + str(i), "test " + str(i), ["sec" + str(i)]))
        db.save_changes()
        # try to retrieve 200 entries
        res = db.get_last_n_elements_with_simple_search(n=tot_line*2)
        self.assertEqual(len(res), tot_line)

        db.close()

    def test_search_by_tag_and_by_description(self):
        """"
        store same command multiple times with different description and tags
        try then to retrieve it
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.output_test_path, self.TEST_DB_FILENAME, None, delete_all_data_from_db=True)
        # insert case 1
        self.assertTrue(db.add_element("ls -ls", "test1", ["security"]))
        self.assertTrue(db.add_element("ls -ls", "test2", None))
        self.assertTrue(db.add_element("ls -ls", "test3", ["sec", "security", "supersecure"]))
        # insert case 2
        self.assertTrue(db.add_element("srm", "", tags=None))
        self.assertTrue(db.add_element("srm", "description command", ["tag-1"]))

        # test case 1
        res = db.get_last_n_elements_with_simple_search(filter="supersecure")
        # check number of matches
        self.assertEqual(len(res), 1)
        # check if tags are saved correctly
        self.assertEqual(res[0][2], "#security#sec#supersecure")
        # check if description is updated
        self.assertEqual(res[0][1], "test3. test2. test1")

        # test case 2 (search for description)
        res = db.get_last_n_elements_with_simple_search(filter="description")
        # check number of matches
        self.assertEqual(len(res), 1)
        # check if tags are saved correctly
        self.assertEqual(res[0][2], "#tag-1")
        # check if description is updated
        self.assertEqual(res[0][1], "description command")

        db.close()

    def test_fill_db_with_wrong_entries(self):
        """"
        store same command multiple times with different description and tags
        try then to retrieve it
        """
        self._set_text_logger()
        db = DatabaseSQLite(self.output_test_path, self.TEST_DB_FILENAME, None, delete_all_data_from_db=True)
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

        db = DatabaseSQLite(self.output_test_path, self.TEST_DB_FILENAME, None, delete_all_data_from_db=True)
        db.add_element("ls", "test", ["sec"])
        db.add_element("ls", "test 2", ["sec"])

        for i in db.get_all_data():
            logging.info(str(i))
        db.close()

    def test_automatic_migration(self):
        """
        test migration from old databse (type 0) to current database

        :return:
        """
        self._set_text_logger()

        # clean test directory
        if os.path.exists(self.output_test_path + self.TEST_DB_FILENAME_OLD):
            os.remove(self.output_test_path + self.TEST_DB_FILENAME_OLD)

        # create old db with structure type 0
        self.conn = sqlite3.connect(self.output_test_path + self.TEST_DB_FILENAME_OLD)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE history 
            (
                command  TEXT,
                counter BIGINT,
                description TEXT,
                tags TEXT
            )
            """)
        # add data with old structure (type 0)
        self.cursor.execute("INSERT INTO history values (?, ?, ?, ?)",
                            ("test1",
                             2,
                             "description",
                             "#tag1#tag2#tag3"
                             ))
        self.cursor.execute("INSERT INTO history values (?, ?, ?, ?)",
                            ("test2",
                             4,
                             "only description",
                             ""
                             ))
        self.cursor.execute("INSERT INTO history values (?, ?, ?, ?)",
                            ("test3",
                             4,
                             "",
                             "#only-tags"
                             ))
        self.conn.commit()
        self.conn.close()

        # initialize new db
        db = DatabaseSQLite(self.output_test_path,
                            self.TEST_DB_FILENAME,
                            [[0, self.TEST_DB_FILENAME_OLD]],  # 0 is the type
                            delete_all_data_from_db=True)
        data = db.get_all_data()

        # check if the number of element matches
        self.assertEqual(len(data), 3)
        # test search for command
        res = db.get_last_n_elements_with_simple_search(filter="test1")
        self.assertEqual(len(res), 1)
        # test search for tag
        res = db.get_last_n_elements_with_simple_search(filter="only-tags")
        self.assertEqual(len(res), 1)
        # test search for description
        res = db.get_last_n_elements_with_simple_search(filter="only description")
        self.assertEqual(len(res), 1)

        # check if migration is successful (true if old file does not exist anymore)
        self.assertFalse(os.path.exists(self.output_test_path + self.TEST_DB_FILENAME_OLD))

    def _set_text_logger(self):
        """
        set global setting of the logging class and print (dynamically) the name of the running test
        :return:
        """
        logging.info("*" * 60)
        # 0 is the current function, 1 is the caller
        logging.info("Start test '" + str(inspect.stack()[1][3]) + "'")
