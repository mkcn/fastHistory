#!/bin/bash

# check if bash or zsh
if [ -n "$BASH_VERSION" ]; then
	_fast_history_project_directory="${BASH_SOURCE[0]%/*}/../";
elif [ -n "$ZSH_VERSION" ]; then
	_fast_history_project_directory="$0:a:h/../";
	echo "zsh detected";
else
	echo "[fastHistory][ERROR] your shell is not supported";
	exit;
fi

# if true the return code of the executed command is check before to store it
# by default this feature is disable
_fast_history_check_return_code=false
_fast_history_bash_debug=false

_fast_history_hooked_cmd=""
_fast_history_short_cmd=false

# define custom function to call the fastHistory in SEARCH mode
f-search() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${_fast_history_hooked_cmd:8 + 1}
    python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "search" "$arguments";
    unset _fast_history_hooked_cmd;
    }

# define an alternative (shorter and faster to type) function to call the fastHistory in SEARCH mode
f() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${_fast_history_hooked_cmd:1 + 1}
    python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "search" "$arguments";
    unset _fast_history_hooked_cmd;
}

# define function to add a command to fastHistory without execute it
f-add() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${_fast_history_hooked_cmd:5 + 1}
    python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "add-explicit" "$arguments";
    unset _fast_history_hooked_cmd;
    }
    
f-import(){
    DIR=$1
    if [ "${DIR:0:1}" = "/" ]; then
        python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "import" "$1";
    else
        python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "import" "$(pwd)/$1";
    fi
}

f-export(){
    if [ $# -eq 0 ]; then
    	python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "export" "fastHistory_$(date +'%Y-%m-%d').db";
    else
    	DIR=$1
    	if [ "${DIR:0:1}" = "/" ]; then
    	    python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "export" "$1";
    	else
    	    python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "export" "$(pwd)/$1";
    	fi
    fi
}

# load bash hook functions
# more info: https://github.com/rcaloras/bash-preexec/
source "$_fast_history_project_directory"bash/bash-preexec.sh

# "preexec" is executed just after a command has been read and is about to be executed
# we store the hooked command in a bash variable
preexec() { _fast_history_hooked_cmd="$1"; }

# "precmd" is executed just before each prompt
# we use the previous hooked command and we store it with fastHistory
# Note: any unsuccessful command (base on the return code '$?') is ignored
precmd() {
	# check if variable is set
	if [[ $_fast_history_hooked_cmd ]]; then
		if ! $_fast_history_check_return_code || [ $? -eq 0 ]; then
		    	# check if the hooked cmd contains the 'comment' char, any command without it will be ignored
		    	# this is just a preliminary check, in the python module a strict regex will be used
		    	# this is only done to avoid to load the python module for each command
		    	if [[ "$_fast_history_hooked_cmd" = *"#"* ]]; then
				python3 "$_fast_history_project_directory"fastHistory/fastHistory.py "add" "$_fast_history_hooked_cmd"
				# clean the cmd, this is needed because precmd can be trigged without preexec (example ctrl+c)
				unset _fast_history_hooked_cmd;
			else
				if $_fast_history_bash_debug ; then echo "[fastHistory][DEBUG] '#' not found: command ignored"; fi;
			fi;
		else
			if $_fast_history_bash_debug ; then echo "[fastHistory][DEBUG] error code detected: command ignored"; fi;
		fi;
	else
		if $_fast_history_bash_debug ; then echo "[fastHistory][DEBUG] _fast_history_hooked_cmd: empty"; fi;
	fi;
     }

