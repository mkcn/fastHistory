#!/bin/bash

FASTHISTORY_PATH_CODE_FOLDER=$HOME"/.fastHistory"
FASTHISTORY_PATH_LOCAL_BIN_FOLDER=$HOME"/.local/bin/"
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

# check if user is root
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
	_fast_history_install_log "info" "bash detected";
	_fast_history_current_folder="${BASH_SOURCE[0]%/*}/";
elif [ -n "$ZSH_VERSION" ]; then
	_fast_history_install_log "info" "zsh detected";
	_fast_history_current_folder="$0:a:h/";
else
	_fast_history_install_log "error" "your shell is not supported (only bash or zsh)";
	exit 1;
fi

# move current context to installer folder
cd "$_fast_history_current_folder" || exit 1

# check if python3 is installed, if not ask to installed.
if python3 --version >/dev/null 2>&1; then
	_fast_history_install_log "info" "python3 detected"
else
	_fast_history_install_log "error" "python3 is missing in your system. Please install it to use fastHistory"
	exit 1
fi


# copy folder fastHistory (only .py, .sh and a couple of configuration files) to ~/.fastHistory
_fast_history_install_log "info" "installation starts"  
rm -f -r "$FASTHISTORY_PATH_CODE_FOLDER" && \
mkdir -p "$FASTHISTORY_PATH_CODE_FOLDER" && \
rsync -R fastHistory/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
rsync -R fastHistory/*/*.py "$FASTHISTORY_PATH_CODE_FOLDER" && \
rsync -R fastHistory/bash/*.sh "$FASTHISTORY_PATH_CODE_FOLDER" && \
rsync -R fastHistory/config/default_fastHistory.conf "$FASTHISTORY_PATH_CODE_FOLDER" && \
rsync -R fastHistory/config/default_version.txt "$FASTHISTORY_PATH_CODE_FOLDER"
# check if all files have been copied
if [ $? -eq 0 ]; then
	_fast_history_install_log "info" "files copied in $FASTHISTORY_PATH_CODE_FOLDER" 
else
	_fast_history_install_log "error" "file copy failed, check the $FASTHISTORY_PATH_CODE_FOLDER folder permissions and try again"
	exit 1
fi

# copy the 'bashlex' third party software to enable the 'man page' feature. this is not mandatory and you can remove this section if you like
if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
	tar -xzf pip/third-party/bashlex-*.tar.gz --directory "$FASTHISTORY_PATH_CODE_FOLDER"
	mv "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/bashlex/ "$FASTHISTORY_PATH_CODE_FOLDER/"
	if rm -r "$FASTHISTORY_PATH_CODE_FOLDER"/bashlex-*/; then
		_fast_history_install_log "info" "bashlex enabled" 
	else
		_fast_history_install_log "error" "tar command failed, check the $FASTHISTORY_PATH_CODE_FOLDER folder permissions and try again"
		exit 1
	fi
elif [[ $YN == "n" || $YN == "N" ]]; then
	_fast_history_install_log "info" "proceeding without bashlex"
else
	_fast_history_install_log "error" "unknown answer, installation stopped"
	exit 1
fi

# create bin file (to emulate the pip installation)
_fast_history_install_log "info" "create bin file in $FASTHISTORY_PATH_LOCAL_BIN_FOLDER$FASTHISTORY_BIN_FILE"  
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




