# fastHistory

A python tool connected to your terminal to store important commands and search them in a new and faster way

![Search sample](images/search.gif)

### Why you need it?

How often do you need to reuse a command but you cannot remember it (or all the needed flags)?

```sh
# example of an 'intuitive' and 'obvious' bash command from my bash history
$ srm -lrvz f1 f2 d1/
```

How many times do you search the same command on Google, over and over? 

> 42 times..  yes..  based on my experience the answer is [42](https://www.independent.co.uk/life-style/history/42-the-answer-to-life-the-universe-and-everything-2205734.html)


And how many times have you told yourself to store this *super* useful command but you didn't? 

> I saved them all ..totally, with a good and detailed explanation for each command

if you know what I am talking about, **fastHistory** is the tool you are looking for!


### The tool

**fastHistory** can save your commands directly from your terminal, all you need is a **#**

```sh
$ srm -lrvz f1 f2 d1/ #
                     /\
                      \------- fastHistory will store "srm -lrvz f1 f2 d1/" in its internal database
```

You can specify one or more **tags**


```sh
$ srm -lrvz f1 f2 d1/ #secure #remove #file #directory
```

or a **description**

```sh
$ srm -lrvz f1 f2 d1/ #@delete file and overwrite it 2 times
```

or **both**

```sh
$ srm -lrvz f1 f2 d1/ #secure #remove #file #directory @delete file and overwrite it 2 times
```

Finally, to search your saved commands, all you need is the **f** of fastHistory

```sh
$ f secure
```

**fastHistory** will then inject the selected command in your terminal input

![Search sample](images/sample.gif)


# How to install

**Warning**: this tool is still under development! A first version will be soon released

1) download this repository
```sh
cd $HOME
git clone https://github.com/mkcn/fastHistory.git
```

2) enable **fastHistory** in your terminal
```sh
echo 'source "$HOME/fastHistory/fastHistory.sh"' >> .bashrc
```

done!


# Commands and syntax

#### Silent adding

```
command_to_save [#[tag [#tag ...]][@description]]
```

#### Explicit adding without execution

```
fadd command_to_save [#[tag [#tag ...]][@description]]
```

#### Simple search 

```
f [filter]
```

**OR search**: match any row where at least one of the following conditions is true:

*  the __filter__ word is contained in the **command** 
*  the __filter__ word is contained in one or more of the **tags**
*  the __filter__ word is contained in the **description**

#### Advanced search
```
f [command_filter] [#tag_filter ...] [@description_filter]
```

**AND search**: match any rows where all the following conditions are true:

*  the __command_filter__ is contained in the **command** 
*  all the __tag_filter__ are contained in the tag list
*  the __description_filter__ is contained in the **description**


License
----

The license for this is the same as that used by GNU bash, GNU GPL v3+.


Copyright
----

The following external projects have been used as part of **fastHistory**:
*  https://github.com/rcaloras/bash-preexec 
    *  **goal**: this bash script is used to hook the commands from the terminal
    *  **code section**: ```bash-preexec.sh```
    *  **changes**: no change
*  https://github.com/idank/bashlex
    *  **goal**: this Python module is used to parse bash commands in order to show info from the man page
    *  **code section**: ```fastHistory/parser/bashlex/```
    *  **changes**: no change 
*  https://github.com/wong2/pick
    *  **goal**: this Python module has been used to select the option from the menu
    *  **code section**: ```fastHistory/pick```
    *  **changes**: all code has been restructured and adapted with a different UI




