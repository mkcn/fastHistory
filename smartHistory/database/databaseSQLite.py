import sqlite3
import logging
import os


class DatabaseSQLite(object):

    databaseFileName = "data/history.db"
    tableName = "history"
    columnName1 = "cmd"
    columnName2 = "description"

    tag_separator = "#"

    def __init__(self, project_path, delete_old_db=False):
        """
        check if database file exit, connect to it and initialize it

        :param project_path:    the current path of the project (used to store the db file)
        :param delete_old_db:   if true the old db file is delete (test purposes)
        """
        self.db_path = project_path + self.databaseFileName
        if delete_old_db:
            self.reset_entire_db()
        init = not os.path.exists(self.db_path)
        self._connect_db(init)

    def _connect_db(self, init=False):
        """
        connect to db
        :param init:    if true the db is initialized
        :return:
        """
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
        logging.info("Create database")
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

    def get_last_N_elements(self, filter=None, n=50):
        """
        get data from db

        :param filter:  string which must match part of the command or description or tag
        :param n:       max number of rows returned
        :return:
        """
        if filter is None:
            self.cursor.execute("SELECT command, description, tags "
                                "FROM history "
                                "ORDER BY rowid DESC LIMIT ?", (n,))
        else:
            self.cursor.execute("SELECT command, description, tags "
                                "FROM history "
                                "WHERE "
                                "command LIKE ? OR "
                                "description LIKE ? OR "
                                "tags LIKE ? "
                                "ORDER BY rowid DESC LIMIT ?", ("%" + filter + "%",
                                                                "%" + filter + "%",
                                                                "%" + filter + "%",
                                                                 n,))
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
        :return:
        """
        # remove whitespaces on the left and right
        cmd = cmd.strip()
        # TODO check if description and tags contains illegal chars (@ and #)

        logging.debug("database - add command: " + str(cmd))
        logging.debug("database - description: " + str(description))
        logging.debug("database - tags: " + str(tags))
        self.cursor.execute("SELECT rowid, counter, description, tags FROM history WHERE Command=?", (cmd,))
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

    def _tags_string_to_array(self, tags_string):
        """
        given the string of tags form the db it split the tags word and put it into an array
        if the string is empty and empty array is returned
        :param tags_string:     #tag1#tag2#tag3
        :return:                ["tag1","tag2","tag3"]
        """
        if tags_string == "":
            return []
        tags = tags_string.split(self.tag_separator)
        if len(tags) >= 2:
            # remove first always empty value
            tags = tags[1:]
            return tags
        else:
            return []

    def _tag_array_to_string(self, tags):
        """
        given a tags array it returns the tags string to store it into the db
        :param tags:
        :return:
        """
        tags_string = ""
        for tag in tags:
            tags_string += self.tag_separator + tag
        return tags_string
