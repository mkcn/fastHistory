

class DatabaseFile(object):
	"""
	TODO implement
	"""

	databaseFileName = "history.txt"

	def __init__(self, project_directory):
		pass

	def get_all_data(self, filter=None):
		return []

	def get_first_50_elements(self, filter=None):
		pass

	def get_last_N_elements(self, filter=None, N=50):
		pass

	def add_element(self, cmd, description, tags ):
		#f = open(self.databaseFileName, "r+")
		pass
