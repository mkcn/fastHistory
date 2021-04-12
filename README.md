
# fastHistory - speed up your terminal!

[![](https://img.shields.io/pypi/status/fastHistory?color=00999b&style=for-the-badge)](https://pypi.org/project/fastHistory/)
[![](https://img.shields.io/pypi/v/fastHistory?color=00999b&style=for-the-badge)](https://pypi.org/project/fastHistory/)
[![](https://img.shields.io/github/last-commit/mkcn/fastHistory?color=00999b&style=for-the-badge)](https://github.com/mkcn/fastHistory/commits)

- [Intro](https://github.com/mkcn/fastHistory/blob/master/README.md#Intro)
- [Supported systems](https://github.com/mkcn/fastHistory/blob/master/README.md#Supported-OSs)
- [Install](https://github.com/mkcn/fastHistory/blob/master/README.md#How-to-install)
- [Update](https://github.com/mkcn/fastHistory/blob/master/README.md#How-to-update)
- [Commands and syntax](https://github.com/mkcn/fastHistory/wiki/Commands-and-syntax)
- [License](https://github.com/mkcn/fastHistory/blob/master/README.md#License)


fastHistory allows you to store, search and automatically paste all the important commands directly in your terminal

![](https://github.com/mkcn/fastHistory/raw/master/images/add_and_search.gif)

# Intro
### Why you need it?

How often do you need to reuse a command but you cannot remember it (with all the needed options/flags)?

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

![](https://github.com/mkcn/fastHistory/raw/master/images/advanced_search.gif)


For each command you can get a quick summary from the man page

**Warning**: this feature does not cover the syntax of all commands

![](https://github.com/mkcn/fastHistory/raw/master/images/man_page.png)

And easily edit the tag and description fields

![](https://github.com/mkcn/fastHistory/raw/master/images/edit_tag.gif)

Furthermore, you can easily export/import all data to make __backups__ or to share your commands with a different machine

```sh
$ f --export
$ f --import fastHistory_2020-03-02.db
```

# Supported OSs

fastHistory can work in any OS with `python3` and a `bash` terminal

`zsh` is also supported!

### List of tested OSs:

| OS         | OS Version | Shell | Python versions | fastHistory version | Test mode | Result | Comment   |
| ---------- |:----------:| ------:|-------------:| -------------------:|----------:| ---------:| ---------:| 
| Ubuntu     | 16.04, 18.04, 20.04* | bash   | 3.6, 3.7, 3.8 | latest | unittest | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  |  * [xclip](https://howtoinstall.co/en/xclip) may need to be installed to enable the copy-to-clipboard feature |
| macOS      | 10.15      | bash   | 3.6, 3.7, 3.8 | latest | unittest | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  | python3 needs to be [installed](https://docs.python-guide.org/starting/install3/osx/)  |
| Fedora     | 29         | bash   | 3.5           | 2.0.0   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> |  pip3 requires the  [`--user` ](https://developer.fedoraproject.org/tech/languages/python/pypi-installation.html) flag |
| Debian     | 9          | bash   | 3.5           | 2.1.3   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> |    |
| Debian     | 10         | zsh*   | 3.7           | 2.0.0   | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%"> | *[syntax limitation](https://github.com/mkcn/fastHistory#Commands-and-syntax)   |
| Windows*   | 10 (1809)  | bash   | 3.6           | 2.2.2  | manual          | <img src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png" width="35%">  | *using the [Windows Subsystem for Linux](https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71) (WSL) you can execute and store [Windows commands](https://docs.microsoft.com/en-us/windows/wsl/interop#run-windows-tools-from-linux) |

# How to install

### Requirements

- `python3`
- `python3-pip` (only for pip3 installation)
    
## Install with pip3

1. `pip3 install fasthistory`
2. `$HOME/.local/bin/f`
3.  close and reopen your terminal

**Note**: be sure to not use `pip` (python2) nor `sudo` (install it only for the current user) 

## Install with installer.sh
 
 1.  download the latest release with this *easy-to-type* link or manually download [it](https://github.com/mkcn/fastHistory/releases)
	 - `wget mkcn.me/f`
 2. extract it
	 -  `tar -xvzf f` 
 3. run the installer with the target user
	- `cd fastHistory-X.X`
	 - `./installer.sh` (this works also offline)
 4. close and reopen your terminal
 5. (optional) delete installation files
 	- `rm -r f fastHistory-X.X`

#### All in one-line

`cd $(mktemp -d /tmp/f.XXXXX) && wget https://mkcn.me/f && tar -xvzf f && ./fastHistory-*/installer.sh && cd -`

# How to update

### Update with f (available from 2.1.1)

 1. `f --update`
 2.  close and reopen your terminal

### Update with pip3
 1. `pip3 install -U --no-cache-dir fasthistory`
 2. `f`
 3.  close and reopen your terminal
 
### Update with installer.sh
 - same steps as [installation](https://github.com/mkcn/fastHistory/blob/master/README.md#Install-with-installersh) 


**Note**: to update from the 1.x.x version your need to follow [these steps](https://github.com/mkcn/fastHistory/wiki/How-to-migrate-from-1.x.x-to-2.x.x) 
 
# How to uninstall

 1. download the installer script and make it executable
	- `wget https://raw.githubusercontent.com/mkcn/fastHistory/master/installer.sh`
	- `chmod +x installer.sh`
 2. run it with the uninstall flag
 	- `./installer.sh -u`

**Note**: `pip3 install fasthistory` is not sufficient to uninstall fastHistory 

# Commands and systax

Find out more about commands and syntax in the [Wiki](https://github.com/mkcn/fastHistory/wiki/Commands-and-syntax) section 

# License

The license for this is the same as that used by GNU bash, GNU GPL v3+.




