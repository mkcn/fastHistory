import logging

from database.InputData import Input
from parser.inputParser import InputParser


class DataManager(object):
	"""
	Class use to manage data and interact with the database
	"""
	MIN_LENGTH_SEARCH_FOR_DESC = 3

	class OPTION:
		INDEX_CMD = 0
		INDEX_DESC = 1
		INDEX_TAGS = 2

	DATABASE_MODE_SQLITE = 0
	DATABASE_MODE_MYSQL = 1

	DUMMY_INPUT_DATA = Input(False, "", [])

	def __init__(self, project_path, db_relative_path, old_db_relative_paths, mode=DATABASE_MODE_SQLITE):
		self.last_search = None
		self.filtered_data = None
		if mode == self.DATABASE_MODE_SQLITE:
			from database.databaseSQLite import DatabaseSQLite
			self.database = DatabaseSQLite(project_path, db_relative_path, old_db_relative_paths)
		else:
			logging.error("database mode not selected")
		# set dummy as default
		self.search_filters = self.DUMMY_INPUT_DATA
		# define special chars based on the chosen database
		self.forbidden_chars = ['\n', '\r', self.database.CHAR_DIVIDER]

	def get_search_filters(self):
		"""
		return parsed filters calculated in the last "filter" call

		:return: [cmd_filter, description_filter, array_tag_filter]
		"""
		return self.search_filters

	def get_forbidden_chars(self):
		"""
		the database uses a special chars and these cannot be use as input to avoid ambiguity
		:return:	array of forbidden chars
		"""
		return self.forbidden_chars

	def filter(self, search, n=100):
		"""
		get filtered commands array
		:param n: 		max number of returned rows
		:param search:	filter text
		:return:		array with [cmd, description, tags array, bool advanced]
		"""
		# put all to lower case
		search = search.lower()

		# parse input search text
		input_data = InputParser.parse_input(search, is_search_cmd=True)

		if input_data:
			self.search_filters = input_data

			if not input_data.is_advanced():
				filtered_data = self.database.get_last_n_filtered_elements(
								generic_filters=input_data.get_main_words(),
								n=n)
			else:
				filtered_data = self.database.get_last_n_filtered_elements(
								generic_filters=input_data.get_main_words(),
								description_filters=input_data.get_description_words(strict=True),
								tags_filters=input_data.get_tags(strict=True),
								n=n)
			if filtered_data:
				return filtered_data
			else:
				return []
		else:
			# the string inserted does not match the regex and a dummy response is returned
			self.search_filters = self.DUMMY_INPUT_DATA
			return []

	def add_new_element(self, cmd, description, tags):
		"""
		add a new command to db
		:param cmd:			bash command
		:param description:	description (or none)
		:param tags:		list of tags (or none)
		:return:			true if value has been stored correctly
		"""
		return self.database.add_element(cmd, description, tags)

	def update_command(self, cmd, new_cmd):
		"""
		update command string of a command
		:param cmd:
		:param new_cmd:
		:return:
		"""
		return self.database.update_command_field(cmd, new_cmd)

	def update_tags(self, cmd, tags):
		"""
		update tag list of a command
		:param cmd:		command to update
		:param tags:	new tag array
		:return:		True is the database was successfully changed, False otherwise
		"""
		return self.database.update_tags_field(cmd, tags)

	def update_description(self, cmd, description):
		"""
		update description of a command
		:param cmd:			command to update
		:param description: new description
		:return:			True is the database was successfully changed, False otherwise
		"""
		return self.database.update_description_field(cmd, description)

	def update_element_order(self, cmd):
		"""
		after a command was selected update the order
		:param cmd:		command to update
		:return:		True is the database was successfully changed, False otherwise
		"""
		return self.database.update_position_element(cmd)

	def delete_element(self, cmd):
		"""
		delete a command from db
		:param cmd:		cmd to delete
		:return:		True is the database was successfully changed, False otherwise
		"""
		return self.database.remove_element(cmd)

	def get_data_from_db(self):
		"""
		this is a SLOW method to call as less as possible
		:param self:
		:return:
		"""
		return self.database.get_all_data()

	def import_data_to_db(self, db_abs_path):
		"""
		import data from old or backed up database file
		:param db_abs_path:	database absolute path
		:return:
		"""
		return self.database.import_external_database(db_abs_path)

