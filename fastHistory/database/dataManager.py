import logging

from parser.inputParser import InputParser


class DataManager(object):
	"""
	Class use to manage data and interact with the database
	"""
	MIN_LENGTH_SEARCH_FOR_DESC = 3

	INDEX_OPTION_CMD = 0
	INDEX_OPTION_DESC = 1
	INDEX_OPTION_TAGS = 2
	INDEX_OPTION_IS_ADVANCED = 3

	DATABASE_MODE_SQLITE = 0
	DATABASE_MODE_MYSQL = 1

	DUMMY_SEARCH_FILTERS = ["", "", [""], False]

	def __init__(self, project_path, db_relative_path, old_db_relative_paths, mode=DATABASE_MODE_SQLITE):
		self.last_search = None
		self.filtered_data = None
		if mode == self.DATABASE_MODE_SQLITE:
			from database.databaseSQLite import DatabaseSQLite
			self.database = DatabaseSQLite(project_path, db_relative_path, old_db_relative_paths)
		else:
			logging.error("database mode not selected")
		# set dummy as default
		self.search_filters = self.DUMMY_SEARCH_FILTERS

	def get_search_filters(self):
		"""
		return parsed filters calculated in the last "filter" call

		:return: [cmd_filter, description_filter, array_tag_filter]
		"""
		return self.search_filters

	def filter(self, search, n=100):
		"""
		get filtered commands array
		:param n: 		max number of returned rows
		:param search:	filter text
		:return:		array with [cmd, description, tags array, bool advanced]
		"""
		# put all to lower case
		search = search.lower()

		# this is a simple optimization
		# basic searches do not contains '@' or '#' (usually)
		# in case of a string such as "echo ' #'" the advance search is called but
		# it will correctly parse it as cmd (without tag or description) because the regex is able to handle such cases
		if InputParser.TAG_SIGN in search or InputParser.DESCRIPTION_SIGN in search:
			filtered_data = self._advanced_search(search, n)
		else:
			filtered_data = self._simple_search(search, n)

		if not filtered_data:
			return []

		new_filtered_data = []
		# tmp solution, change the type here
		for i in range(len(filtered_data)):
			tags_str = filtered_data[i][2]
			tags = tags_str.split("#")
			# remove first empty item
			if len(tags) > 0 and tags[0] == "":
				tags = tags[1:]
			new_filtered_data.append([filtered_data[i][0], filtered_data[i][1], tags])

		return new_filtered_data

	def _simple_search(self, search, n):
		self.search_filters = None
		filtered_data = self.database.get_last_n_elements_with_simple_search(filter=search, n=n)
		# [False] is used as bool to indicate an "advance search result"
		self.search_filters = [search, search, [search], False]
		return filtered_data

	def _advanced_search(self, search, n):

		sections = InputParser.parse_cmd(search, is_search_cmd=True)

		logging.debug("advance search: " + str(sections))

		if sections:
			filtered_data = self.database.get_last_n_elements_with_advanced_search(
				cmd_filter=sections[InputParser.INDEX_CMD],
				description_filter=sections[InputParser.INDEX_DESC],
				tags_filter=sections[InputParser.INDEX_TAGS],
				n=n)
			#  the bool to indicate if it is an "advance search result"
			if sections[InputParser.INDEX_DESC] is None and sections[InputParser.INDEX_TAGS] == []:
				# if no description and no tags then the result must be consider a simple research
				self.search_filters = sections + [False]
			else:
				self.search_filters = sections + [True]

			return filtered_data
		else:
			# the string inserted does not match the regex and a dummy response is returned
			self.search_filters = self.DUMMY_SEARCH_FILTERS
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
