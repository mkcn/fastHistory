import os
import re
import datetime
from shutil import copyfile, move


class SetupManager:

	def __init__(self, logger_console, project_directory, configuration_file, version_file="version.txt", home_path=None):
		self.logger_console = logger_console
		self.project_directory = project_directory	
		self.configuration_file =  configuration_file
		self.version_file = version_file 
		self.default_prefix = "default_"
		self.current_script_path = os.path.dirname(os.path.realpath(__file__))
		if home_path is None:
			self.home_path = os.environ['HOME'] + "/"
		else:
			self.home_path = home_path

		hook_bash_path = os.path.dirname(self.current_script_path) + "/bash/f.sh"
		self.hook_updated_str = "source \"" + hook_bash_path + "\""

	def handle_setup(self):

		if not self.create_folder():
			return False

		if not self.setup_rc_file():
			return False
		
		if not self.copy_default_file(self.current_script_path + "/" + self.default_prefix + self.configuration_file , self.project_directory + self.configuration_file):
			return False
	
		if not self.copy_default_file(self.current_script_path + "/" + self.default_prefix + self.version_file , self.project_directory + self.version_file):
			return False
				
		self.logger_console.log_on_console_info("setup completed")
		return True

	def get_hook_str(self):
		return self.hook_updated_str

	def copy_default_file(self, file_default, file_output):
		if not os.path.isfile(file_output):
			if os.path.isfile(file_default):
				self.logger_console.log_on_console_info("copy file from: " + file_default)
				copyfile(file_default, file_output)
			else:
				self.logger_console.log_on_console_error("default file not found: "+ file_default)
				return False
		return True

	def create_folder(self):
		if not os.path.isdir(self.project_directory):
			os.mkdir(self.project_directory)
			if os.path.isdir(self.project_directory):
				self.logger_console.log_on_console_info("created project folder: " + self.project_directory)
			else:
				self.logger_console.log_on_console_error("it is not possible to create the folder: " + self.project_directory)
				return False
		return True

	def auto_setup(self):
		self.logger_console.log_on_console_error("environment not correctly configured")
		res=input("do you want to configure/fix it? [y/n]: ")
		if (res.lower() == "y"):
			if self.handle_setup():
				self.logger_console.log_on_console_info("setup completed. Please restart your terminal. ")
			else:
				self.logger_console.log_on_console_error("setup failed")
		else:
			self.logger_console.log_on_console_error("nothing done")

	def setup_rc_file(self):
		bashrc_path = self.home_path + ".bashrc"
		zshrc_path = self.home_path + ".zshrc"
		
		if not self.check_for_source_string(bashrc_path) and not self.check_for_source_string(zshrc_path):
			self.logger_console.log_on_console_error("neither .bashrc nor .zshrc have been found") # TODO change
			return False
		else:
			self.logger_console.log_on_console_info("hook setup correctly for current user") # TODO change
			return True

	def check_for_source_string(self, file_path_in):
		self.logger_console.log_on_console_info("setup: " + file_path_in)
		if os.path.isfile(file_path_in):
			self.logger_console.log_on_console_info("rc file found")
			file_path_out = file_path_in + ".fastHistory.tmp"
			fin = open(file_path_in, "r")
			# TODO , remove tmp file or make sure it is not opened in append mode
			fout = open(file_path_out, "w")

			pattern = re.compile("^source .*/fastHistory.*/bash/f.sh.*")
			found_hook_updated = False
			found_hook_old = False
			for line in fin:
				res = pattern.match(line)
				if res is not None:
					if res.group() == self.hook_updated_str:
						found_hook_updated = True
					else:
						found_hook_old = True
				else:
					fout.write(line)
			fout.write("\n")
			fout.write(self.hook_updated_str)
			fout.truncate()
			fout.close()
			fin.close()

			if found_hook_updated and not found_hook_old:
				self.logger_console.log_on_console_info("hook setup already setup")
				if os.path.isfile(file_path_out):
					os.remove(file_path_out)
				return True
			else:
				self.logger_console.log_on_console_info("hook need to be setup/update")
				dt = datetime.datetime.now()
				nowms = str(dt.microsecond)

				file_path_in_tmp = file_path_in + "-" + nowms + ".fastHistory.backup"
				if os.path.isfile(file_path_in_tmp):
					self.logger_console.log_on_console_error("cannot overwrite backup file, try again")
					return False
				move(file_path_in, file_path_in_tmp)
				move(file_path_out, file_path_in)

				with open(file_path_in, 'r') as f:
					lines = f.read().splitlines()
					last_line = lines[-1]
					if last_line == self.hook_updated_str:
						self.logger_console.log_on_console_info("bash hook set correctly")
						if os.path.isfile(file_path_in_tmp):
							os.remove(file_path_in_tmp)
						if os.path.isfile(file_path_out):
							os.remove(file_path_out)
						return True
					else:
						self.logger_console.log_on_console_error("something went wrong and bash hook has not been set")
						self.logger_console.log_on_console_error("a backup file can be found here: " + file_path_in_tmp)
						# TODO explain better
						return False
			return False
		else:
			return False



