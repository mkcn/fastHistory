import sqlite3
import logging
import os


class DatabaseSQLite(object):

    TABLE_NAME = "history"
    COLUMN_CMD = "cmd"
    COLUMN_DESCRIPTION = "description"
    COLUMN_TAGS = "tags"

    CHAR_TAG = "#"
    CHAR_DESCRIPTION = "@"
    EMPTY_STRING = ""

    def __init__(self, db_path, delete_old_db=False):
        """
        check if database file exit, connect to it and initialize it

        :param db_path:         the current path of the project (used to store the db file)
        :param delete_old_db:   if true the old db file is delete (test purposes)
        """
        self.db_path = db_path
        if delete_old_db:
            self.reset_entire_db()
        self._connect_db()

    def _connect_db(self):
        """
        connect to db and create it if it does not exit

        :return:
        """
        init = not os.path.isfile(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        if init:
            self._create_db()
            self.save_changes()

    def save_changes(self):
        """
        after each change to the db a save must be done

        :return:
        """
        self.conn.commit()

    def reset_entire_db(self):
        """
        for debug and test purposes delete the db file

        :return:
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def close(self):
        """
        close connection to db

        :return:
        """
        self.conn.close()

    def _create_db(self):
        """
        create table to store commands
        Note: this table results to be the most efficient tested structure to fast filter data
        the "tags" column is composed by the concatenation of single 'tag' string separated by a #
        because during the search procedure the # cannot be used this will result an optimized string search
        without false positives
        example     command, counter, description, tags
                    ls 1     2        info         #file#list#disk
                    srm -r   1        delete file  #secure#remove

                search with filter value = "list"
                result:
                    ls 1     2        info         #file#list#disk

        :return:
        """
        logging.info("create database")
        self.cursor.execute("""
        CREATE TABLE history 
        (
            command  TEXT,
            counter BIGINT,
            description TEXT,
            tags TEXT
        )
        """)
        # note: sqlite automatically adds a column called "rowID"
        # the "rowID" value is a 64-bit signed integers

    def get_all_data(self, filter=None):
        self.cursor.execute("SELECT * FROM history ")
        return self.cursor.fetchall()

    def get_last_n_elements_with_simple_search(self, filter=None, n=50):
        """
        get data from db
        by default if a simple search is done, the string is searched in all values: cmd, tags and description

        :param filter:  string which must match part of the command or description or tag
        :param n:       max number of rows returned
        :return:       filtered data (array of array [command, description, tags])
        """

        if filter is None or filter == DatabaseSQLite.EMPTY_STRING:
            query = "SELECT command, description, tags " \
                                "FROM history " \
                                "ORDER BY rowid DESC LIMIT ?"
            parameters = (n,)
        else:
            query = "SELECT command, description, tags " \
                     "FROM history " \
                     "WHERE " \
                     "command LIKE ? OR " \
                     "description LIKE ? OR " \
                     "tags LIKE ? " \
                     "ORDER BY rowid DESC LIMIT ?"
            parameters = ("%" + filter + "%",  "%" + filter + "%", "%" + filter + "%", n,)

        # execute query
        self.cursor.execute(query, parameters)

        logging.debug("simple search query: " + query + " - " + str(parameters))

        return self.cursor.fetchall()

    def get_last_n_elements_with_advanced_search(self, cmd_filter=None, description_filter=None, tags_filter=None, n=50):
        """
        get data from db
        this is a more specific and advanced search
        the there are 6 different combination of searching:
            - cmd
            - description
            - tag (single or multiple)
            - cmd + description
            - cmd + tag(s)
            - desc + tag(s)
        all filters are combined dynamically with "AND" logic

        note: when tag or description are empty, we search for any "not" empty" line (search for # -> all cmd with tags are shown)

        :param cmd_filter:          string to filter cmd
        :param description_filter:  string to filter documentation
        :param tags_filter:         array of string to filter
        :param n:                   max number of rows returned
        :return:                    filtered data (array of array [command, description, tags])
        """
        parameters = ()
        and_needed = False

        # select
        query = "SELECT command, description, tags FROM history WHERE "

        if cmd_filter is not None and len(cmd_filter) > 0:
            query += "command LIKE ? "
            parameters += ("%" + cmd_filter + "%", )
            and_needed = True

        if description_filter is not None:
            if and_needed:
                query += "AND "
            else:
                and_needed = True
            if description_filter == DatabaseSQLite.EMPTY_STRING:
                query += "description <> '' "
                parameters += ()
            else:
                query += "description LIKE ? "
                parameters += ("%" + description_filter + "%", )

        if tags_filter is not None:
            for tag_filter in tags_filter:
                if and_needed:
                    query += "AND "
                else:
                    and_needed = True

                if tag_filter == DatabaseSQLite.EMPTY_STRING:
                    query += "tags <> '' "
                    parameters += ()
                else:
                    query += "tags LIKE ? "
                    parameters += ("%%" + tag_filter + "%", )

        # sort
        query += "ORDER BY rowid DESC LIMIT ?"
        parameters += (n, )

        # execute query
        self.cursor.execute(query, parameters)

        logging.debug("advance search query: " + query + " - " + str(parameters))

        return self.cursor.fetchall()

    def add_element(self, cmd, description=None, tags=None):
        """
        insert a new element in the database,
        if it already in the db just increase the counter
        if the description is different it updates it
        if there are new tags it updates the tags string

        :param cmd:             bash command
        :param description:     description
        :param tags:            array of tag
        :return:                true if the command has been store successfully
        """
        # remove whitespaces on the left and right
        cmd = cmd.strip()

        # check if description and tags contains an illegal char (@ or #)
        if description is not None and (self.CHAR_TAG in description or self.CHAR_DESCRIPTION in description):
            logging.error("description contains illegal char " + self.CHAR_DESCRIPTION + ": " + description)
            return False
        if tags is not None and type(tags) == list:
            for tag in tags:
                if self.CHAR_TAG in tag or self.CHAR_DESCRIPTION in tag:
                    logging.error("tags contains illegal char " + self.CHAR_DESCRIPTION + ": " + tag)
                    return False

        logging.debug("database - add command: " + str(cmd))
        logging.debug("database - description: " + str(description))
        logging.debug("database - tags: " + str(tags))
        self.cursor.execute("SELECT rowid, counter, description, tags FROM history WHERE command=?", (cmd,))
        matches = self.cursor.fetchall()
        matches_number = len(matches)
        if matches_number == 0:
            if description is None:
                description = ""
            tags_str = self._tag_array_to_string(tags)
            self.cursor.execute("INSERT INTO history values (?, ?, ?, ?)", (cmd, 0, description, tags_str,))
            logging.debug("database - added NEW command")
        elif matches_number == 1:
            match = matches[0]
            # get old values
            match_id = match[0]
            match_counter = int(match[1])
            match_desc = match[2]
            match_tags_str = match[3]

            # set new counter
            new_counter = match_counter + 1
            # set new description
            if description is not None and description is not "" and description != match_desc:
                # TODO possible improvement: keep (or ask to keep) also the previous description
                new_description = description
            else:
                new_description = match_desc
            # set new tags list
            if tags is not None and type(tags) == list and len(tags) > 0:
                update_tags = False
                match_tags = self._tags_string_to_array(match_tags_str)
                for tag in tags:
                    if tag not in match_tags and tag != "":
                        # new tag
                        match_tags.append(tag)
                        update_tags = True
                if update_tags:
                    new_tags_str = self._tag_array_to_string(match_tags)
                else:
                    new_tags_str = match_tags_str
            else:
                new_tags_str = match_tags_str

            # delete old row
            self.cursor.execute("DELETE FROM history WHERE rowid=?", (match_id,))

            logging.debug("new_tags_str: " + str(new_tags_str))
            # create new row which will have the highest rowID (last used command)
            self.cursor.execute("INSERT INTO history values (?, ?, ?, ?)", (
                cmd,
                new_counter,
                new_description,
                new_tags_str,))
            logging.error("database - command updated: " + cmd)

        else:
            logging.error("database - command entry is not unique: " + cmd)
            return False

        self.save_changes()
        return True

    def remove_element(self, cmd):
        """
        delete specific command from database

        :param cmd:     cmd to delete
        :return:        true is successfully deleted, false otherwise
        """
        logging.info("delete command: " + str(cmd))
        if cmd is None:
            logging.error("remove_element: " + "cmd is None")
            return False
        # remove whitespaces on the left and right
        cmd = cmd.strip()
        if len(cmd) == 0:
            logging.error("remove_element: " + "cmd is empty")
            return False

        # delete item
        self.cursor.execute("DELETE FROM history WHERE  command=?", (cmd,))
        self.save_changes()
        logging.info("delete completed")
        return True

    def _tags_string_to_array(self, tags_string):
        """
        given the string of tags form the db it split the tags word and put it into an array
        if the string is empty and empty array is returned

        :param tags_string:     #tag1#tag2#tag3
        :return:                ["tag1","tag2","tag3"]
        """
        if tags_string == "":
            return []
        tags = tags_string.split(self.CHAR_TAG)
        if len(tags) >= 2:
            # remove first always empty value
            tags = tags[1:]
            return tags
        else:
            return []

    def _tag_array_to_string(self, tags):
        """
        given a tags array it returns the tags string to store it into the db
        note: empty tag are not stored

        :param tags:
        :return:
        """
        tags_string = ""
        for tag in tags:
            if len(tag) > 0:
                tags_string += self.CHAR_TAG + tag
        return tags_string
