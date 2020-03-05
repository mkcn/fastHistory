#!/bin/bash

############################################################
# tool: fastHistory
# note: this script must be called with "source <file>" 
# author: Mirko Conti
# date: 2019-07-24
############################################################

_fast_history_bash_debug=true

_fast_history_hooked_cmd=""
_fast_history_short_cmd=false
# [sperimental feature, off by default] if true the return code of the executed command is check before to store it
_fast_history_check_return_code=false
_fast_history_executable="f"

# define internal log function 
_fast_history_log() {
	if [ "$1" = "error" ]; then
		echo "[fastHistory][ERROR] $2";  
	elif  [ "$1" = "info" ]; then
		echo "[fastHistory][INFO ] $2"; 
	elif [ "$1" = "debug" ] && $_fast_history_bash_debug ; then
		echo "[fastHistory][DEBUG] $2";
	fi
}

# start message
_fast_history_log "debug" "loading fastHistory start..";

# check if bash or zsh
if [ -n "$BASH_VERSION" ]; then
	_fast_history_log "debug" "bash detected";
	_fast_history_project_directory="${BASH_SOURCE[0]%/*}/../";
elif [ -n "$ZSH_VERSION" ]; then
	_fast_history_log "debug" "zsh detected";
	_fast_history_project_directory="$0:a:h/../";
else
	_fast_history_log "error" "your shell is not supported";
	return 1;
fi

# check environment
if [ -s "$_fast_history_project_directory"../fastHistory/__init__.py ]; then
	_fast_history_log "debug" "installation folder: $_fast_history_project_directory";
else
	_fast_history_log "error" "cannot find installation folder";
	return 1;
fi

# share variable with python to find any inconsistency between the bash hook and the installation folder
export _fast_history_project_directory
_fast_history_log "debug" "_fast_history_project_directory exported";

# load bash hook functions (more info: https://github.com/rcaloras/bash-preexec/)
source "$_fast_history_project_directory"bash/bash-preexec.sh;
if [ -z "$__bp_imported" ]; then
	_fast_history_log "error" "preexec cannot be loaded";
	return 1;
else
	_fast_history_log "debug" "preexec loaded correctly";
fi

# check if $PATH is correctly set 
_fast_history_local_bin=$HOME/.local/bin
if [ -f $_fast_history_local_bin/$_fast_history_executable ]; then
	if echo "$PATH" | grep -q -F $_fast_history_local_bin; then 
		_fast_history_log "debug" "$_fast_history_local_bin is already in your PATH variable";
	else
		export PATH=$PATH:$_fast_history_local_bin
		_fast_history_log "debug" "$_fast_history_local_bin has been added to your PATH variable";
	fi
fi

# "preexec" is executed just after a command has been read and is about to be executed
# we store the hooked command in a bash variable
preexec() {
	_fast_history_hooked_cmd="$1";
	# TODO move this to python context, not sure
	if [[ "$_fast_history_hooked_cmd" == "#"* ]]; then
		# remove the intial #
		_fast_history_hooked_cmd="${_fast_history_hooked_cmd:1}"
		echo "f.sh-this command will be saved but NOT executed!: '$_fast_history_hooked_cmd'" ;
	else
		echo "f.sh-this command will may be saved AND executed!: '$_fast_history_hooked_cmd'" ;
	fi
}


# "precmd" is executed just before each prompt
# we use the previous hooked command and we store it with fastHistory
# Note: any unsuccessful command (base on the return code '$?') is ignored
precmd() {
	# check if variable is set
	if [[ $_fast_history_hooked_cmd ]]; then
		if ! $_fast_history_check_return_code || [ $? -eq 0 ]; then
		    	# check if the hooked cmd contains the 'comment' char, any command without it will be ignored
			# check also if the command is fasthistory itself (e.g. 'f #test' should not be stored)
		    	# this is just a preliminary check, in the python module a strict regex will be used
		    	# this is only done to avoid to load the python module for each command
		    	if [[ "$_fast_history_hooked_cmd" == *"#"* ]] && [[ "$_fast_history_hooked_cmd" != "$_fast_history_executable "* ]] ; then
				$_fast_history_executable --add-from-bash "$_fast_history_hooked_cmd"
				# clean the cmd, this is needed because precmd can be trigged without preexec (example ctrl+c)
				unset _fast_history_hooked_cmd;
			else	
				_fast_history_log "debug" "shell command ignored";
			fi;
		else
			_fast_history_log "debug" "error code detected: command ignored";
		fi;
	fi;
     }

_fast_history_log "debug" "loading fastHistory completed. Use 'f' to start"; 

