#!/bin/bash

############################################################
# tool: fastHistory
# note: this script must be called with "source <file>" 
# author: Mirko Conti
# date: 2020-03
############################################################

# enable this to debug the bash hook of fastHistory
_fast_history_bash_debug=false

_fast_history_hooked_cmd=""
_fast_history_short_cmd=false
# [sperimental feature, off by default] if true the return code of the executed command is check before to store it
_fast_history_check_return_code=false
_fast_history_executable="f"

# define internal log function 
_fast_history_log() {
	if [ "$1" = "error" ]; then
		printf "[\033[0;31mfastHistory\033[0m][bash] $2\n";
	elif [ "$1" = "debug" ] && $_fast_history_bash_debug ; then
		printf "[\033[0;36mfastHistory\033[0m][bash] $2\n";
	fi
}

# start message
_fast_history_log "debug" "loading bash hook..";

# check if bash or zsh
if [ -n "$BASH_VERSION" ]; then
	_fast_history_log "debug" "bash detected";
	_fast_history_path_code_folder="${BASH_SOURCE[0]%/*}/../";
elif [ -n "$ZSH_VERSION" ]; then
	_fast_history_log "debug" "zsh detected";
	_fast_history_path_code_folder="$0:a:h/../";
else
	_fast_history_log "error" "shell not supported, only bash and zsh are allowed";
	return 1;
fi

# check environment
if [ -s "$_fast_history_path_code_folder"../fastHistory/__init__.py ]; then
	_fast_history_log "debug" "folder: $_fast_history_path_code_folder";
else
	_fast_history_log "error" "cannot find installation folder";
	return 1;
fi

# share variable with python to find any inconsistency between the bash hook and the installation folder
export _fast_history_path_code_folder
_fast_history_log "debug" "_fast_history_path_code_folder exported";

# load bash hook functions (more info: https://github.com/rcaloras/bash-preexec/)
source "$_fast_history_path_code_folder"bash/bash-preexec.sh;
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
		_fast_history_log "debug" "$_fast_history_local_bin already in PATH variable";
	else
		export PATH=$PATH:$_fast_history_local_bin
		_fast_history_log "debug" "$_fast_history_local_bin added to PATH variable";
	fi
else
	_fast_history_log "debug" "$_fast_history_local_bin/$_fast_history_executable does not exist (this may be an issue)";
fi

# "preexec" is executed just after a command has been read and is about to be executed
# we store the hooked command in a bash variable

export _fast_history_hooked_cmd

preexec() {
	_fast_history_hooked_cmd="$1";
	if [[ "$_fast_history_hooked_cmd" == "#"* ]]; then
		# remove the intial '#'
		_fast_history_hooked_cmd="${_fast_history_hooked_cmd:1}"
		_fast_history_log "debug" "command will not be executed!"
	fi
}

# "precmd" is executed just before each prompt
# we use the previous hooked command and we store it with fastHistory
# Note: any unsuccessful command (base on the return code '$?') is ignored
precmd() {
	# check if variable is not empty
	if [ -n "$_fast_history_hooked_cmd" ]; then
		if ! $_fast_history_check_return_code || [ $? -eq 0 ]; then
		    # check if the hooked cmd contains the 'comment' char, any command without it will be ignored
			  # check also if the command is fasthistory itself (e.g. 'f #test' should not be stored)
		    # this is just a preliminary check, in the python module a strict regex will be used
		    # this is only done to avoid to load the python module for each command
		    if [[ "$_fast_history_hooked_cmd" == *"#"* ]] && [[ "$_fast_history_hooked_cmd" != "$_fast_history_executable "* ]] ; then
          $_fast_history_executable --add-explicit "$_fast_history_hooked_cmd"
          # clean the cmd, this is needed because precmd can be trigged without preexec (example ctrl+c)
          _fast_history_hooked_cmd="";
        else
          _fast_history_log "debug" "command ignored";
        fi;
		else
			_fast_history_log "debug" "error code detected: command ignored";
		fi;
	fi;
     }

_fast_history_log "debug" "loading fastHistory completed, use 'f' to start"; 

