
FASTHISTORY_FOLDER_CODE=$HOME"/.fastHistory"
FASTHISTORY_FOLDER_BIN=$HOME"/.local/bin/"
FASTHISTORY_BIN_FILE="f"
FASTHISTORY_OLD_DB_RELATIVE_PATH="data/*.db"


# define internal log function
_fast_history_install_log() {
	if [ "$1" = "error" ]; then
		printf "[\033[0;31minstaller\033[0m] $2\n";
	elif [ "$1" = "info" ] ; then
		printf "[\033[0;36minstaller\033[0m] $2\n";
	elif [ "$1" = "warn" ] ; then
		printf "[\033[1;33minstaller\033[0m] $2\n";
	fi
}

# check if user is root 
if [ "$EUID" -eq 0 ]; then
	read -p "Warning: it is not advised to install fastHistory with a root account. Do you want to interrupt the installation? [Y/n] " YN
	if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
		_fast_history_install_log "info" "installation stopped"
		return
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
	_fast_history_installation_directory="${BASH_SOURCE[0]%/*}/";
elif [ -n "$ZSH_VERSION" ]; then
	_fast_history_install_log "info" "zsh detected";
	_fast_history_installation_directory="$0:a:h/";
else
	_fast_history_install_log "error" "your shell is not supported (only bash or zsh)";
	exit 1;
fi

# check if python3 is installed, if not ask to installed.
python3 --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
	_fast_history_install_log "info" "python3 detected"
else
	_fast_history_install_log "error" "python3 is missing in your system. Please install it to use fastHistory"
	exit 1
fi


# copy folder fastHistory (only .py, .sh and a couple of configuration files) to ~/.fastHistory
_fast_history_install_log "info" "installation starts"  
rm -f -r $FASTHISTORY_FOLDER_CODE && \
mkdir -p $FASTHISTORY_FOLDER_CODE && \
cp --parents $_fast_history_installation_directory/fastHistory/*.py $FASTHISTORY_FOLDER_CODE && \
cp --parents $_fast_history_installation_directory/fastHistory/*/*.py $FASTHISTORY_FOLDER_CODE && \
cp --parents $_fast_history_installation_directory/fastHistory/bash/*.sh $FASTHISTORY_FOLDER_CODE && \
cp --parents $_fast_history_installation_directory/fastHistory/config/default_fastHistory.conf $FASTHISTORY_FOLDER_CODE && \
cp --parents $_fast_history_installation_directory/fastHistory/config/default_version.txt $FASTHISTORY_FOLDER_CODE
# check if all files have been copied
if [ $? -eq 0 ]; then
	_fast_history_install_log "info" "files copied in $FASTHISTORY_FOLDER_CODE" 
else
	_fast_history_install_log "error" "file copy failed, check the $FASTHISTORY_FOLDER_CODE folder permissions and try again"
	exit 1
fi

# copy the 'bashlex' third party software to enable the 'man page' feature. this is not mandatory and you can remove this section if you like
if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
	tar -xzf $_fast_history_installation_directory/pip/third-party/bashlex-*.tar.gz --directory $FASTHISTORY_FOLDER_CODE
	mv $FASTHISTORY_FOLDER_CODE/bashlex-*/bashlex/ $FASTHISTORY_FOLDER_CODE/
	rm -r $FASTHISTORY_FOLDER_CODE/bashlex-*/
	if [ $? -eq 0 ]; then
		_fast_history_install_log "info" "bashlex enabled" 
	else
		_fast_history_install_log "error" "tar command failed, check the $FASTHISTORY_FOLDER_CODE folder permissions and try again"
		exit 1
	fi
elif [[ $YN == "n" || $YN == "N" ]]; then
	_fast_history_install_log "info" "proceeding without bashlex"
else
	_fast_history_install_log "error" "unknown answer, installation stopped"
	exit 1
fi

# create bin file (to emulate the pip installation)
_fast_history_install_log "info" "create bin file in $FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE"  
mkdir -p $FASTHISTORY_FOLDER_CODE
printf "#!$(which python3)
# -*- coding: utf-8 -*-
import re
import sys

sys.path.insert(1, '$FASTHISTORY_FOLDER_CODE')
from fastHistory import f

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(f())
" > $FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE

# we need to make it executable and call it
chmod +x $FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE

# run setup fastHistory
if [[ -f "$FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE" ]]; then
	$FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE --setup
else
	_fast_history_install_log "error" "Installation failed"
	_fast_history_install_log "error" "Please check the $FASTHISTORY_FOLDER_CODE folder permissions and try again"
	exit 1
fi

# TODO import data from old db if found
#if [[ -f "$_fast_history_installation_directory$FASTHISTORY_OLD_DB_RELATIVE_PATH" ]]; then
#	# for each file ask to import 
#	$FASTHISTORY_FOLDER_BIN$FASTHISTORY_BIN_FILE --import  DB_FILE_NAME
#else
#	echo "No old db found failed"
#	echo "You can manually import them with \"f --import <path .db file>\"" 
#fi


_fast_history_install_log "info" "Installation completed"




