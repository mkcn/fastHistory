

class DataManager(object):
	"""
	TODO rewrite and describe
	"""

	MIN_LENGTH_SEARCH_FOR_DESC = 3

	INDEX_OPTION_CMD = 0
	INDEX_OPTION_TAGS = 1
	INDEX_OPTION_DESC = 2

	DATABASE_MODE_FILE = 0
	DATABASE_MODE_SQLITE = 1
	DATABASE_MODE_MYSQL = 2

	def __init__(self, project_path, mode=DATABASE_MODE_FILE):
		self.last_search = None
		self.filtered_data = None
		if mode == self.DATABASE_MODE_SQLITE:
			from database.databaseSQLite import DatabaseSQLite
			self.database = DatabaseSQLite(project_path)
		elif mode == self.DATABASE_MODE_MYSQL:
			from database.databaseMYSQL import DatabaseMYSQL
			self.database = DatabaseMYSQL(project_path)
		else:  # file mode as default
			from database.databaseFile import DatabaseFile
			self.database = DatabaseFile(project_path)

	def filter(self, search, n=100):
		"""
		get filtered commands array
		:param n: 		max number of returned rows
		:param search:	filter text
		:return:		array with [cmd, tags, description]
		"""
		# put all to lower case
		search = search.lower()

		# TODO set bool to check or not the description
		# len(search) >= self.MIN_LENGTH_SEARCH_FOR_DESC

		filtered_data = self.database.get_last_N_elements(filter=search, n=n)

		new_filtered_data = []
		# tmp change type
		for i in range(len(filtered_data)):
			tags_str = filtered_data[i][2]
			tags = tags_str.split("#")
			# remove first empty item
			if len(tags) > 0 and tags[0] == "":
				tags = tags[1:]
			new_filtered_data.append([filtered_data[i][0], tags, filtered_data[i][1]])

		"""
		# when the new search work start with the old one we can filter the old filter data
		# if not the data must be reloaded
		if self.last_search is None or not search.startswith(self.last_search):
			self.filtered_data = self.get_data_from_db()
		# use previous filtered data set
		search_field = self.filtered_data

		res = []
		for i in range(len(search_field)):
			cmd = search_field[i][0]
			tags = search_field[i][1]
			desc = search_field[i][2]
			if search in cmd.lower():
				# log_info("found match: cmd")
				res.append(search_field[i])
			elif len(search) >= self.MIN_LENGTH_SEARCH_FOR_DESC and search in desc.lower():
				# log_info("found match: desc")
				res.append(search_field[i])
			else:
				for j in range(len(tags)):
					if search in tags[j].lower():
						# log_info("found match: tag")
						res.append(search_field[i])
						break
		self.filtered_data = res
		"""
		return new_filtered_data

	def add_new_element(self, cmd, description, tags):
		self.database.add_element(cmd, description, tags)

	def get_data_from_db(self):
		"""
		this is a SLOW method to call as less as possible
		:param self:
		:return:
		"""
		# TODO read from disk or db query
		return self.database.get_all_data()
