
# fastHistory 2.0 - speed up your terminal!


| <img src="https://github.githubassets.com/images/icons/emoji/unicode/26a0.png" width="6%"> WARNING: this is a beta version |
|:---------------------------|

- [Intro](https://github.com/mkcn/fastHistory/tree/pip#Intro)
- [Supported systems](https://github.com/mkcn/fastHistory/tree/pip#Supported-OSs)
- [How to install](https://github.com/mkcn/fastHistory/tree/pip#How-to-install)
- [Commands and syntax](https://github.com/mkcn/fastHistory/tree/pip#Commands-and-syntax)
- [License](https://github.com/mkcn/fastHistory/tree/pip#License)


A python tool connected to your terminal to store important commands, search them in a fast way and automatically paste them into your terminal

![](https://github.com/mkcn/fastHistory/raw/pip/images/add_and_search.gif)


# Intro
### Why you need it?

How often do you need to reuse a command but you cannot remember it (or all the needed options/flags)?

```sh
# example of a common but not so 'easy-to-remember' bash command from my bash history
$ tar -xvzf file.tar.gz
```

How many times do you search the same commands on Google, over and over? 

> 42 times..  yes..  based on my experience the answer is [42](https://www.independent.co.uk/life-style/history/42-the-answer-to-life-the-universe-and-everything-2205734.html)


And how many times have you told yourself to store this *super* useful command but you didn't? 

> I saved them all ..totally, with a good and detailed explanation for each command

if you know what I am talking about, **fastHistory** is the tool you are looking for!


### Usage sample

**fastHistory** can save your commands directly from your terminal, all you need is a **#**

```sh
$ tar -xvzf file.tar.gz #
                       /\
                        \-- fastHistory will store 'tar -xvzf file.tar.gz' in its internal database
```

You can specify one or more **tags**


```sh
$ tar -xvzf file.tar.gz #untar #extract #archive 
```

or a **description**

```sh
$ tar -xvzf file.tar.gz #@extract compressed files from archive
```

or **both**

```sh
$ tar -xvf archive.tar.gz #untar @extract compressed files from archive
```

To search the saved commands, all you need is **f**
and the selected command wiil be **automatically pasted** into your terminal!

```sh
$ f
```

![](https://github.com/mkcn/fastHistory/raw/pip/images/advanced_search.gif)


For each command you can get a quick summary from the man page

**Warning**: this feature currently does not cover the syntax of all commands

![](https://github.com/mkcn/fastHistory/raw/pip/images/man_page.png)

And easily edit the tag and description fields

![](https://github.com/mkcn/fastHistory/raw/pip/images/edit_tag.gif)

Furthermore, you can easily export/import all data to make __backups__ or to share your commands with a different machine

```sh
$ f --export
$ f --import fastHistory_2020-03-02.db
```

# Supported OSs

fastHistory can work in any OS with `python3` and a `bash` terminal

note: `zsh` is also supported!

### List of tested OSs:

| OS         | OS Version | Shell | Python versions | fastHistory version | Test mode | Result | Comment   |
| ---------- |:----------:| ------:|-------------:| -------------------:|----------:| ---------:| ---------:| 
| Ubuntu     | 16.04      | bash   | 3.6, 3.7, 3.8 | latest | unittest | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  |    |
| Ubuntu     | 18.04      | bash   | 3.6, 3.7, 3.8 | latest | unittest | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  |    |
| macOS      | 10.15      | bash   | 3.6, 3.7, 3.8 | latest | unittest | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  | python3 needs to be [installed](https://docs.python-guide.org/starting/install3/osx/)  |
| Fedora     | 29         | bash   | 3.5           | 2.0.0   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> |    |
| Debian     | 9          | bash   | 3.5           | 2.0.0   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> |    |
| Debian     | 10         | zsh*   | 3.7           | 2.0.0   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> | *[syntax limitation](https://github.com/mkcn/fastHistory/tree/pip#Commands-and-syntax)   |
| Windows*   | 10 (1809)  | bash   | 3.6           | 2.0.0  | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  | *using the [Ubuntu terminal for Windows](https://ubuntu.com/tutorials/tutorial-ubuntu-on-windows) |

# How to install

### Requirements

- `python3`
- `python3-pip` (not needed for offline installation)
    
## Install with pip3

1. `pip3 install fasthistory`
2. `f` 

**Note**: be sure to not use `sudo` nor `pip (version 2)`

**Note**: if `f` command is not found, the first time you need to use `~./local/bin/f` instead

## Install in offline mode

 1.  download the latest release with this *easy-to-type* link or manually download [it](https://github.com/mkcn/fastHistory/releases)
	 - `wget mkcn.me/f`
 2. (if needed) move it to the remote/offline machine
 3. unzip it
	 -  `tar -xvzf f` 
 4. run the installer with the target user
	- `cd fastHistory-X.X`
	 - `./installer.sh`

**Note**: all the downloaded files can be deleted after the installation is completed

# How to update

### Update pip3
 - `pip3 install -U fasthistory`
 
### Update offline mode
 - same steps as installation 

### Update old git clone
 - `git pull`
 - `./installer.sh`
 
# How to uninstall

 1. download the installer script (only for pip mode)
	- `wget https://raw.githubusercontent.com/mkcn/fastHistory/pip/installer.sh`
 2. make it executable and run it with the uninstall flag
	- `chmod +x installer.sh`
 	- `./installer.sh -u`

**Note**: `pip3 install fasthistory` is not sufficient to uninstall fastHistory 

# Commands and syntax

#### Simple adding

```
<command_to_save> #[<tag> [#<tag> ...]][@<description>]
```

#### Adding without execution

```
f --add <command> #[<tag> [#<tag> ...]][@<description>]
```
or 
```
# <command_to_save> #[<tag> [#<tag> ...]][@<description>]
```

Note: the latter is not available with `zsh`

![](https://github.com/mkcn/fastHistory/raw/pip/images/add_without_execute_and_search_cut.gif)

#### Simple search 

```
f [<filter>]
```

**OR search**: match any row where **at least one** of the following conditions is true:

* the __filter__ words are contained in the **command** 
* the __filter__ words are contained in the **tags** list
* the __filter__ words are contained in the **description**

#### Advanced search
```
f [<filter>] [#<tag_filter> ...] [@<description_filter>]
```

**AND search**: match any rows where **all** the following conditions are true:

* the __filter__ words are contained in the **command** OR **tags** OR **description**
* the __tag_filter__ words are contained in the **tag** list
* the __description_filter__ words contained in the **description**

![](https://github.com/mkcn/fastHistory/raw/pip/images/f_advanced_search_cut.gif)

#### Export database
```
f --export [<output_name>]
```
* the __output__ is the file name of the output database (this parameter is optional)

#### Import external database
```
f --import <input_name>
```

* the __input_name__ is the file name of the input database (e.g. fastHistory_2019-03-23.db)

#### Change fastHistory configuration
```
f --config
```

#### Force a fastHistory setup to fix possible issues
```
f --setup
```

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




