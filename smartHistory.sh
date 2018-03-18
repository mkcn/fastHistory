#!/bin/bash

# absolute path of the Smart History project
# NOTE: change this with YOUR project path
project_directory="$HOME/smartHistory"

smart_history_hook_enable=true
smart_history_hooked_cmd=""
smart_history_short_cmd=false

# define custom function to call the SmartHistory in SEARCH mode
hsearch() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$project_directory"/smartHistory/smartHistory.py "search" "$arguments";
    smart_history_hook_enable=false;
    }

# define an alternative (shorter) function to call the SmartHistory in SEARCH mode
:() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$project_directory"/smartHistory/smartHistory.py "search" "$arguments";
    smart_history_hook_enable=false;
}

# define function to add a command to SmartHistory without execute it
hadd() {
    # trick to capture all input (otherwise the comments are removed)
    arguments=${smart_history_hooked_cmd:${#FUNCNAME[0]} + 1}
    python3 "$project_directory"/smartHistory/smartHistory.py "add" "$arguments";
    smart_history_hook_enable=false;
    }

# load bash hook functions
# more info: https://github.com/rcaloras/bash-preexec/
source "$project_directory"/bash-preexec.sh

# "preexec" is executed just after a command has been read and is about to be executed
# we store the hooked command in a bash variable
preexec() { smart_history_hooked_cmd="$1"; }

# "precmd" is executed just before each prompt
# we use the previous hooked command and we store it with SmartHistory
# Note: any unsuccessful command (base on the return command '$?') is ignored
precmd() {
        if [ $? -eq 0 ]; then
            if [ "$smart_history_hook_enable" = true ] ; then
                # spawn thread in a subshell, to not affect the response time of the bash command
                (python3 "$project_directory"/smartHistory/smartHistory.py "add-silent" "$smart_history_hooked_cmd" &)
            else
            	smart_history_hook_enable=true;
            fi ;
        fi;
     }

