#!/bin/bash

FASTHISTORY_PATH_CODE_FOLDER=$HOME"/.fastHistory"
FASTHISTORY_PATH_DATA_FOLDER=$HOME"/.local/share/fastHistory"
FASTHISTORY_PATH_LOCAL_BIN_FOLDER=$HOME"/.local/bin/"
FASTHISTORY_PATH_BASHRC=$HOME"/.bashrc"
FASTHISTORY_PATH_ZSHRC=$HOME"/.zshrc"
FASTHISTORY_BIN_FILE="f"
FASTHISTORY_PATH_RELATIVE_OLD_DB="data/fh_v1.db"


# define internal log function
_fast_history_install_log() {
	if [ "$1" = "error" ]; then
		printf "[\033[0;31minstaller\033[0m] %s\n" "$2";
	elif [ "$1" = "info" ] ; then
		printf "[\033[0;36minstaller\033[0m] %s\n" "$2";
	elif [ "$1" = "warn" ] ; then
		printf "[\033[1;33minstaller\033[0m] %s\n" "$2";
	fi
}

if [ -z "$1" ]; then
	## install fastHistory
	if [ "$EUID" -eq 0 ]; then
		_fast_history_install_log "error" "it is not advised to install fastHistory with a root account"
		read -r -p "do you want to interrupt the installation? [Y/n] " YN
		if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
			_fast_history_install_log "info" "installation stopped"
			exit 1
		elif [[ $YN == "n" || $YN == "N" ]]; then
			_fast_history_install_log "info" "proceeding with root.."
		else
			_fast_history_install_log "error" "unknown answer, installation stopped"
			exit 1
		fi
	fi

	# check if bash or zsh
	if [ -n "$BASH_VERSION" ]; then
		_fast_history_install_log "info" "bash: ok";
		_fast_history_current_folder="${BASH_SOURCE[0]%/*}/";
	elif [ -n "$ZSH_VERSION" ]; then
		_fast_history_install_log "info" "zsh: ok";
		_fast_history_current_folder="$0:a:h/";
	else
		_fast_history_install_log "error" "your shell is not supported (only bash or zsh)";
		exit 1;
	fi

	# move current context to installer folder
	cd "$_fast_history_current_folder" || exit 1

	# check if python3 is installed, if not ask to installed.
	if python3 --version >/dev/null 2>&1; then
		_fast_history_install_log "info" "python3: ok"
	else
		_fast_history_install_log "error" "python3 is missing in your system. Please install it to use fastHistory"
		exit 1
	fi


	# copy folder fastHistory (only .py, .sh and a couple of configuration files) to ~/.fastHistory
	# try 'cp parents' or the equivalent 'rsync' to copy file structure
	if command -v rsync >/dev/null 2>&1; then
	  rm -f -r "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  mkdir -p "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync -R fastHistory/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync -R fastHistory/*/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync -R fastHistory/bash/*.sh "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync -R fastHistory/config/default_fastHistory.conf "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync -R fastHistory/config/default_version.txt "$FASTHISTORY_PATH_CODE_FOLDER"
	else
	  rm -f -r "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  mkdir -p "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/*/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/bash/*.sh "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/config/default_fastHistory.conf "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/config/default_version.txt "$FASTHISTORY_PATH_CODE_FOLDER"
	fi
	# check if all files have been copied
	if [ $? -eq 0 ]; then
		_fast_history_install_log "info" "code copied: $FASTHISTORY_PATH_CODE_FOLDER" 
	else
		_fast_history_install_log "error" "code copy failed, check the '$FASTHISTORY_PATH_CODE_FOLDER' folder permissions and try again"
		exit 1
	fi

	# copy the 'bashlex' third party software to enable the 'man page' feature. this is not mandatory and you can remove this section if you like
	if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
		tar -xzf pip/third-party/bashlex-*.tar.gz --directory "$FASTHISTORY_PATH_CODE_FOLDER"
		mv "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/bashlex/ "$FASTHISTORY_PATH_CODE_FOLDER/"
		if rm -r "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/; then
			_fast_history_install_log "info" "bashlex: enabled" 
		else
			_fast_history_install_log "error" "tar command failed, check the '$FASTHISTORY_PATH_CODE_FOLDER' folder permissions and try again"
			exit 1
		fi
	elif [[ $YN == "n" || $YN == "N" ]]; then
		_fast_history_install_log "info" "proceeding without bashlex"
	else
		_fast_history_install_log "error" "unknown answer, installation stopped"
		exit 1
	fi

	# create bin file (to emulate the pip installation)
	_fast_history_install_log "info" "bin file: $FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"  
	mkdir -p "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER"
	printf "#!%s
# -*- coding: utf-8 -*-
import re
import sys

sys.path.insert(1, '%s')
from fastHistory import f

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(f())
" "$(command -v python3)" "$FASTHISTORY_PATH_CODE_FOLDER"> "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"

	# we need to make it executable and call it
	chmod +x "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"

	# run setup fastHistory
	if [[ -f "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE" ]]; then
		"$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE" --setup --from-installer
	else
		_fast_history_install_log "error" "Installation failed"
		_fast_history_install_log "error" "Please check the $FASTHISTORY_PATH_CODE_FOLDER folder permissions and try again"
		exit 1
	fi

	# import data from old db if found
	if [[ -f "$FASTHISTORY_PATH_RELATIVE_OLD_DB" ]]; then
		last_modified_date=$(date -r $FASTHISTORY_PATH_RELATIVE_OLD_DB "+%Y-%m-%d %H:%M:%S")
		_fast_history_install_log "info" "old database file: $_fast_history_current_folder$FASTHISTORY_PATH_RELATIVE_OLD_DB"
		_fast_history_install_log "info" "old database last change: $last_modified_date" 
		read -r -p "old fastHistory database found, do you want to import it? [Y/n] " YN
		if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
			"$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE" --import $FASTHISTORY_PATH_RELATIVE_OLD_DB --from-installer
		elif [[ $YN == "n" || $YN == "N" ]]; then
			_fast_history_install_log "info" "proceeding without import"
		else
			_fast_history_install_log "error" "unknown answer, installation stopped"
			exit 1
		fi
	fi
	_fast_history_install_log "info" "Installation completed"
else
	if [ "$1" == "-u" ] || [ "$1" == "--uninstall" ]; then
	  default_answer=$2
		uninstall_correct=true
		uninstall_already_done=true
		source_str_regex="^source\ .*\/fastHistory.*\/bash\/f.sh.*"

		_fast_history_install_log "info" "uninstall.."

		if [[ -d "$FASTHISTORY_PATH_DATA_FOLDER" ]]; then
			uninstall_already_done=false
			_fast_history_install_log "info" "data folder found: $FASTHISTORY_PATH_DATA_FOLDER"
			if [ "$default_answer" == "--yes-delete-everything" ]; then
			    YN="y"
			else
			    _fast_history_install_log "warn" "it is strongly suggested to make a backup (e.g. using 'f --export') before proceeding further"
			    read -r -p "do you want delete NOW all stored commands and configurations? [y/N] " YN
			fi
			if [[ $YN == "y" || $YN == "Y" ]]; then
				if rm -r "$FASTHISTORY_PATH_DATA_FOLDER"; then
					_fast_history_install_log "info" "deleted data folder: $FASTHISTORY_PATH_DATA_FOLDER"
				else
					uninstall_correct=false
					_fast_history_install_log "error" "cannot delete data folder: $FASTHISTORY_PATH_DATA_FOLDER"
				fi

			elif [[ $YN == "n" || $YN == "N" || $YN == "" ]]; then
				_fast_history_install_log "info" "data kept: $FASTHISTORY_PATH_DATA_FOLDER"
				read -r -p "do you want to proceed with the fastHistory code removal? [y/N] " YN
				if [[ $YN == "Y" || $YN == "y" ]]; then
					_fast_history_install_log "info" "proceed.."
				else
					_fast_history_install_log "info" "script stopped"
					exit 1		
				fi		
			else
				_fast_history_install_log "error" "unknown answer, script stopped"
				exit 1
			fi
		fi
		
		if [[ -f "$FASTHISTORY_PATH_BASHRC" ]] && ! sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_BASHRC" | diff -q "$FASTHISTORY_PATH_BASHRC" - > /dev/null 2>&1; then
			uninstall_already_done=false
			if sed -e "s/$source_str_regex//g" -i "$FASTHISTORY_PATH_BASHRC"; then
				_fast_history_install_log "info" "deleted bash hook from: $FASTHISTORY_PATH_BASHRC"
			else
				uninstall_correct=false
				_fast_history_install_log "error" "bash hook found but not deleted from: $FASTHISTORY_PATH_BASHRC"
			fi
		fi

		if [[ -f "$FASTHISTORY_PATH_ZSHRC" ]] && ! sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_ZSHRC" | diff -q "$FASTHISTORY_PATH_ZSHRC" - > /dev/null 2>&1; then
			uninstall_already_done=false
			if sed -e "s/$source_str_regex//g" -i "$FASTHISTORY_PATH_ZSHRC"; then
				_fast_history_install_log "info" "deleted zsh hook from: $FASTHISTORY_PATH_ZSHRC"
			else
				uninstall_correct=false
				_fast_history_install_log "error" "zsh hook found but not deleted from: $FASTHISTORY_PATH_ZSHRC"
			fi
		fi
		
		if command -v pip3 >/dev/null 2>&1 && pip3 show fastHistory >/dev/null 2>&1; then
			uninstall_already_done=false
			if pip3 uninstall -y fastHistory; then
				_fast_history_install_log "info" "pip package 'fastHistory' found and deleted"
			else
				uninstall_correct=false
				_fast_history_install_log "error" "pip package 'fastHistory' found but not uninstalled correctly"
			fi
		fi

		if [[ -d "$FASTHISTORY_PATH_CODE_FOLDER" ]]; then
			uninstall_already_done=false
			if rm -r "$FASTHISTORY_PATH_CODE_FOLDER"; then
				_fast_history_install_log "info" "deleted code folder: $FASTHISTORY_PATH_CODE_FOLDER"
			else
				uninstall_correct=false
				_fast_history_install_log "error" "cannot delete code folder: $FASTHISTORY_PATH_CODE_FOLDER"
			fi	
		fi

		if [[ -f "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE" ]]; then
			uninstall_already_done=false
			if rm "$FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"; then
				_fast_history_install_log "info" "deleted bin file: $FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"
			else
				uninstall_correct=false
				_fast_history_install_log "error" "cannot delete bin file: $FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"
			fi
		fi
			
		if $uninstall_already_done; then
			_fast_history_install_log "info" "fastHistory not found, nothing to do"
		elif $uninstall_correct; then
			_fast_history_install_log "info" "fastHistory has been uninstalled"
		else
			_fast_history_install_log "warn" "fastHistory partially uninstalled"
		fi
	else
		echo "Usage:" 
		echo "    ./installer [-u] [--yes-delete-everything]"
		echo "Sample:"
		echo "    run './install' to install fastHistory"
		echo "    run './install -u' to uninstall it"
		echo "    run './install -u --yes-delete-everything' to uninstall it without interactive questions (not recommended)"
	fi
fi



