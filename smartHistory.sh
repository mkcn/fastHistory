#!/bin/bash

# absolute path of the Smart History folder
smart_history_project_directory="${BASH_SOURCE[0]%/*}"

# if true the return code of the executed command is check before to store it
# by default this feature is disable
smart_history_check_return_code=false
smart_history_debug=false

smart_history_hooked_cmd=""
smart_history_short_cmd=false

# define custom function to call the SmartHistory in SEARCH mode
hsearch() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$smart_history_project_directory"/smartHistory/smartHistory.py "search" "$arguments";
    unset smart_history_hooked_cmd;
    }

# define an alternative (shorter) function to call the SmartHistory in SEARCH mode
:() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$smart_history_project_directory"/smartHistory/smartHistory.py "search" "$arguments";
    unset smart_history_hooked_cmd;
}

# define function to add a command to SmartHistory without execute it
hadd() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$smart_history_project_directory"/smartHistory/smartHistory.py "add" "$arguments";
    unset smart_history_hooked_cmd;
    }

# load bash hook functions
# more info: https://github.com/rcaloras/bash-preexec/
source "$smart_history_project_directory"/bash-preexec.sh

# "preexec" is executed just after a command has been read and is about to be executed
# we store the hooked command in a bash variable
preexec() { smart_history_hooked_cmd="$1"; }

# "precmd" is executed just before each prompt
# we use the previous hooked command and we store it with SmartHistory
# Note: any unsuccessful command (base on the return code '$?') is ignored
precmd() {
	# check if variable is set
	if [[ $smart_history_hooked_cmd ]]; then
		if ! $smart_history_check_return_code || [ $? -eq 0 ]; then
		    	# check if the hooked cmd contains the comment char, any command without it will be ignored
		    	# this is just a preliminary check, a further regex check will be done by the python module
		    	if [[ "$smart_history_hooked_cmd" = *"#"* ]]; then
				# spawn thread in a subshell, to not affect the response time of the bash command
				(python3 "$smart_history_project_directory"/smartHistory/smartHistory.py "add-silent" "$smart_history_hooked_cmd" &)
				# clean the cmd, this is needed because precmd can be trigged without preexec (example ctrl+c)
				unset smart_history_hooked_cmd;
			else
				if $smart_history_debug ; then echo "[SmartHistory][DEBUG] '#' not found: command ignored"; fi;
			fi;
		else
			if $smart_history_debug ; then echo "[SmartHistory][DEBUG] error code detected: command ignored"; fi;
		fi;
	else
		if $smart_history_debug ; then echo "[SmartHistory][DEBUG] smart_history_hooked_cmd: empty"; fi;
	fi;
     }

