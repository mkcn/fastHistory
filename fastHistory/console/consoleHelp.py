"""
help menu of fastHistory
"""

HELP_STR="""Usage: 
  <command_to_save> #[<tag> [#<tag> ...]][@<description>]
  # <command_to_save> #[<tag> [#<tag> ...]][@<description>]
  f [<filter>] [#<tag_filter> ...] [@<description_filter>]
  f [OPTION]
  
fastHistory connected to your terminal to store important commands, 
search them in a fast way and automatically paste them into your terminal.

Store examples:
  tar -xvf f.tar.gz #untar @extract compressed files from archive
  ls -lsa #show #all #files

Search examples:
  f tar                        # search all stored command related to tar
  f #untar                     # search all stored command with the 'unzip' tag
  f --export                   # export all stored command 
  f --import 2019-03-23.db     # export all stored command 

OPTIONS
  -v, --version                show current version
  -h, --help                   show this help message
  -a, --add <command> #        add command (same as '# <command_to_save> #')
  --export [<output_name>]     export database with all stored commands
  --import <input_name>        import commands from exported database
                                the commands will be imported only if not already present
                                if same command has different tag or description they will be merged 
  --config                     change configuration file
  --setup                      re-run the setup, possibly to repair fastHistory

"""
