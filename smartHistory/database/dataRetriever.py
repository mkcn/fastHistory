from database.sampleDB import DB_SAMPLE


class DataRetriever(object):
	"""
	TODO rewrite and describe
	"""

	MIN_LENGTH_SEARCH_FOR_DESC = 3

	INDEX_OPTION_CMD = 0
	INDEX_OPTION_TAGS = 1
	INDEX_OPTION_DESC = 2

	def __init__(self):
		self.last_search = None
		self.filtered_data = None

	def filter(self, search):
		"""
		get filtered commands array
		:param search:
		:return:		array with [cmd, tags, description]
		"""
		# put all to lower case
		search = search.lower()
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
		return res

	def get_data_from_db(self):
		"""
		this is a SLOW method to call as less as possible
		:param self:
		:return:
		"""
		# TODO read from disk or db query
		return DB_SAMPLE
