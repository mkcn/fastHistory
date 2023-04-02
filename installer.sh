#!/bin/bash

FASTHISTORY_PATH_CODE_FOLDER=$HOME"/.fastHistory"
FASTHISTORY_PATH_DATA_FOLDER=$HOME"/.local/share/fastHistory"
FASTHISTORY_PATH_LOCAL_BIN_FOLDER=$HOME"/.local/bin/"
FASTHISTORY_PATH_BASHRC=$HOME"/.bashrc"
FASTHISTORY_PATH_ZSHRC=$HOME"/.zshrc"
FASTHISTORY_BIN_FILE="f"


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


	# copy folder fastHistory (only .py, .sh, a couple of configuration and license files) to ~/.fastHistory
	# note: macOS does not support "cp -r"
	# try 'cp parents' (linux) or the equivalent 'rsync' (macOS) to copy file structure
	if command -v rsync >/dev/null 2>&1; then
	  rm -f -r "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  mkdir -p "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative fastHistory/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative fastHistory/*/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative fastHistory/bash/*.sh "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative fastHistory/config/default_fastHistory.conf "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative fastHistory/config/default_version.txt "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  rsync --relative LICENSE "$FASTHISTORY_PATH_CODE_FOLDER"/fastHistory/ && \
	  rsync --relative --recursive fastHistory/tldr/tldr/ "$FASTHISTORY_PATH_CODE_FOLDER"/
	else
	  rm -f -r "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  mkdir -p "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/*/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/bash/*.sh "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/config/default_fastHistory.conf "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents fastHistory/config/default_version.txt "$FASTHISTORY_PATH_CODE_FOLDER" && \
	  cp --parents LICENSE "$FASTHISTORY_PATH_CODE_FOLDER"/fastHistory/ && \
	  cp --parents --recursive fastHistory/tldr/tldr/ "$FASTHISTORY_PATH_CODE_FOLDER"/
	fi
	# check if all files have been copied
	if [[ $? -eq 0 && -f "$FASTHISTORY_PATH_CODE_FOLDER"/fastHistory/LICENSE ]]; then
		_fast_history_install_log "info" "code copied: $FASTHISTORY_PATH_CODE_FOLDER" 
	else
		_fast_history_install_log "error" "code copy failed, check the '$FASTHISTORY_PATH_CODE_FOLDER' folder permissions and try again"
		exit 1
	fi

  # check if the 'ls' TLDR page has been correctly copied
	if [[ -f "$FASTHISTORY_PATH_CODE_FOLDER"/fastHistory/tldr/tldr/pages/common/ls.md ]]; then
			_fast_history_install_log "info" "TLDR pages: enabled"
		else
			_fast_history_install_log "error" "TLDR pages not enabled, check the '$FASTHISTORY_PATH_CODE_FOLDER/fastHistory/tldr/tldr/' folder"
			exit 1
	fi

	# copy the third party software ('bashlex', 'pyperclip') to enable the 'man page' feature
	# NOTE: FastHistory will run even without these extra code, but some feature will not work
	if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
	  # source: https://github.com/idank/bashlex/releases/ (tag 0.15)
		tar -xzf pip/third-party/bashlex-*.tar.gz --directory "$FASTHISTORY_PATH_CODE_FOLDER"
		mv "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/bashlex/ "$FASTHISTORY_PATH_CODE_FOLDER/"
		mv "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/LICENSE "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex/
		rm -r "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/

	  # source: https://github.com/asweigart/pyperclip/blob/master/src/pyperclip/__init__.py (pip 1.8.2 - commit 76e2dcb13c4eb26d97a9c41a6a20d5b2e2f87ef5)
	  #         https://github.com/asweigart/pyperclip/blob/master/LICENSE.txt (pip 1.8.2 - commit 76e2dcb13c4eb26d97a9c41a6a20d5b2e2f87ef5)
	  mkdir "$FASTHISTORY_PATH_CODE_FOLDER"/pyperclip
		cp pip/third-party/pyperclip/*  "$FASTHISTORY_PATH_CODE_FOLDER"/pyperclip/

		if [[ -f "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex/__init__.py ]]; then
			_fast_history_install_log "info" "bashlex: enabled" 
		else
			_fast_history_install_log "error" "bashlex not enabled, check the '$FASTHISTORY_PATH_CODE_FOLDER' folder permissions and try again"
			exit 1
		fi

		if [[ -f "$FASTHISTORY_PATH_CODE_FOLDER"/pyperclip/__init__.py ]]; then
			_fast_history_install_log "info" "pyperclip: enabled"
		else
			_fast_history_install_log "error" "pyperclip not enabled, check the '$FASTHISTORY_PATH_CODE_FOLDER' folder permissions and try again"
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

	_fast_history_install_log "info" "installation completed"
	_fast_history_install_log "warn" "please restart your terminal and then use 'f' to start"
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
			if sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_BASHRC" > "$FASTHISTORY_PATH_BASHRC".tmp && mv "$FASTHISTORY_PATH_BASHRC".tmp "$FASTHISTORY_PATH_BASHRC"; then
			  if ! sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_BASHRC" | diff -q "$FASTHISTORY_PATH_BASHRC" - > /dev/null 2>&1; then
					uninstall_correct=false
				  _fast_history_install_log "error" "bash hook found but removal failed: $FASTHISTORY_PATH_BASHRC"
				else
          _fast_history_install_log "info" "deleted bash hook from: $FASTHISTORY_PATH_BASHRC"
				fi
			else
				uninstall_correct=false
				_fast_history_install_log "error" "bash hook found but not deleted from: $FASTHISTORY_PATH_BASHRC"
			fi
		fi

		if [[ -f "$FASTHISTORY_PATH_ZSHRC" ]] && ! sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_ZSHRC" | diff -q "$FASTHISTORY_PATH_ZSHRC" - > /dev/null 2>&1; then
			uninstall_already_done=false
			if sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_ZSHRC" > "$FASTHISTORY_PATH_ZSHRC".tmp && mv "$FASTHISTORY_PATH_ZSHRC".tmp "$FASTHISTORY_PATH_ZSHRC"; then
        if ! sed -e "s/$source_str_regex//g" "$FASTHISTORY_PATH_ZSHRC" | diff -q "$FASTHISTORY_PATH_ZSHRC" - > /dev/null 2>&1; then
					uninstall_correct=false
				  _fast_history_install_log "error" "zsh hook found but removal failed: $FASTHISTORY_PATH_ZSHRC"
				else
          _fast_history_install_log "info" "deleted zsh hook from: $FASTHISTORY_PATH_ZSHRC"
				fi
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
			exit 0
		elif $uninstall_correct; then
			_fast_history_install_log "info" "fastHistory has been uninstalled"
			exit 0
		else
			_fast_history_install_log "warn" "fastHistory partially uninstalled"
			exit 1
		fi
	else
		echo "Usage:  " 
		echo "    ./installer [-u] [--yes-delete-everything]"
		echo "Sample:"
		echo "    run './install' to install fastHistory"
		echo "    run './install -u' to uninstall it"
		echo "    run './install -u --yes-delete-everything' to uninstall it without interactive questions (not recommended)"
	fi
fi



