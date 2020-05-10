import os
import re
import datetime
from shutil import copyfile, move


class SetupManager:

	def __init__(self, logger_console, path_data_folder, path_code_folder, configuration_file, version_file, home_path=None):
		self.logger_console = logger_console
		self.path_data_folder = path_data_folder
		self.configuration_file = configuration_file
		self.version_file = version_file 
		self.default_prefix = "default_"

		self.path_code_folder = path_code_folder
		if home_path is None:
			self.home_path = os.environ['HOME'] + "/"
		else:
			self.home_path = home_path

		hook_bash_path = self.path_code_folder + "/bash/f.sh"
		self.hook_updated_str = "source \"" + hook_bash_path + "\""

	def handle_setup(self):

		if not self.create_folder():
			return False

		if not self.setup_rc_file():
			return False
		
		if not self.copy_default_file(self.path_code_folder + "/config/" + self.default_prefix + self.configuration_file, self.path_data_folder + self.configuration_file):
			return False
	
		if not self.copy_default_file(self.path_code_folder + "/config/" + self.default_prefix + self.version_file, self.path_data_folder + self.version_file, overwrite=True):
			return False

		return True

	def get_hook_str(self):
		return self.hook_updated_str

	def copy_default_file(self, file_default, file_output, overwrite=False):
		file_output_exits = os.path.isfile(file_output)
		file_default_exits = os.path.isfile(file_default)

		if overwrite or not file_output_exits:
			if file_default_exits:
				if file_output_exits:
					os.remove(file_output)
				copyfile(file_default, file_output)
			else:
				self.logger_console.log_on_console_error("default file not found: " + file_default)
				return False
		return True

	def create_folder(self):
		if not os.path.isdir(self.path_data_folder):
			os.makedirs(self.path_data_folder)
			if os.path.isdir(self.path_data_folder):
				self.logger_console.log_on_console_info("created project folder: " + self.path_data_folder)
			else:
				self.logger_console.log_on_console_error("it is not possible to create the folder: " + self.path_data_folder)
				return False
		return True

	def auto_setup(self, reason=None, force=False):
		if reason is None:
			question_str = "-"
			pass
		elif reason[0] is True:
			self.logger_console.log_on_console_warn(reason[1])
			question_str = "do you want to proceed? [Y/n]: "
		elif reason[0] is False:
			self.logger_console.log_on_console_error(reason[1])
			question_str = "do you want to try to fix it automatically? [Y/n]: "
		elif reason[0] is None:
			self.logger_console.log_on_console_error(reason[1])
			return False
		else:
			self.logger_console.log_on_console_error("corner case not handled")
			return False

		if force:
			answer = True
		else:
			res = input(question_str)
			answer = (res.lower() == "y" or res == "")

		if answer:
			if self.handle_setup():
				self.logger_console.log_on_console_info("setup completed")
				return True
			else:
				self.logger_console.log_on_console_error("setup failed")
				return False
		else:
			self.logger_console.log_on_console_error("nothing done")
			return False

	def setup_rc_file(self):
		bashrc_path = self.home_path + ".bashrc"
		zshrc_path = self.home_path + ".zshrc"
		bash_found = False
		bash_result = False
		zsh_found = False
		zsh_result = False

		if os.path.isfile(bashrc_path):
			bash_found = True
			bash_result = self.check_for_source_string(bashrc_path)

		if os.path.isfile(zshrc_path):
			zsh_found = True
			zsh_result = self.check_for_source_string(zshrc_path)
		
		if not bash_found and not zsh_found:
			self.logger_console.log_on_console_error("neither" + bashrc_path + " nor " + zshrc_path + " have been found. Please check your system")
			return False
		else:
			# if a file exists the result must be true
			return (not bash_found or bash_result) and (not zsh_found or zsh_result)

	def check_for_source_string(self, file_path_in):
		self.logger_console.log_on_console_info("setup: " + file_path_in)
		file_path_out = file_path_in + ".fastHistory.tmp"
		fin = open(file_path_in, "r")
		fout = open(file_path_out, "w")

		pattern = re.compile("^source .*/fastHistory.*/bash/f.sh.*")
		found_hook_updated = False
		found_hook_old = False
		is_last_line_empty = False
		for line in fin:
			res = pattern.match(line)
			if res is not None:
				if res.group() == self.hook_updated_str:
					found_hook_updated = True
				else:
					found_hook_old = True
			else:
				fout.write(line)
				if len(line.strip()) == 0:
					is_last_line_empty = True
				else:
					is_last_line_empty = False
		if not is_last_line_empty:
			fout.write("\n")
		fout.write(self.hook_updated_str)
		fout.truncate()
		fout.close()
		fin.close()

		if found_hook_updated and not found_hook_old:
			self.logger_console.log_on_console_info("hook already present")
			if os.path.isfile(file_path_out):
				os.remove(file_path_out)
			return True
		else:
			dt = datetime.datetime.now()
			nowms = str(dt.microsecond)

			file_path_in_tmp = file_path_in + "-" + nowms + ".fastHistory.backup"
			if os.path.isfile(file_path_in_tmp):
				self.logger_console.log_on_console_error("backup file already exist '%s', try again" % file_path_in_tmp)
				if os.path.isfile(file_path_out):
					os.remove(file_path_out)
				return False
			move(file_path_in, file_path_in_tmp)
			move(file_path_out, file_path_in)

			with open(file_path_in, 'r') as f:
				lines = f.read().splitlines()
				last_line = lines[-1]
				if last_line == self.hook_updated_str:
					if found_hook_old:
						self.logger_console.log_on_console_info("hook updated")
					else:
						self.logger_console.log_on_console_info("hook added")
					if os.path.isfile(file_path_in_tmp):
						os.remove(file_path_in_tmp)
					if os.path.isfile(file_path_out):
						os.remove(file_path_out)
					return True
				else:
					self.logger_console.log_on_console_error("something went wrong and hook has not been set in " + file_path_in)
					self.logger_console.log_on_console_error("a backup file can be found here: " + file_path_in_tmp)
					return False
		return False



