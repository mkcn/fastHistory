# rsync
> Transfer files either to or from a remote host (not between two remote hosts).
> Can transfer single files, or multiple files matching a pattern.
> More information: <https://manned.org/rsync>.

- Transfer file from local to remote host
`rsync {{path/to/local_file}} {{remote_host}}:{{path/to/remote_directory}}`

- Transfer file from remote host to local
`rsync {{remote_host}}:{{path/to/remote_file}} {{path/to/local_directory}}`

- Transfer file in archive (to preserve attributes) and compressed (zipped) mode with verbose and human-readable Progress
`rsync -azvhP {{path/to/local_file}} {{remote_host}}:{{path/to/remote_directory}}`

- Transfer a directory and all its children from a remote to local
`rsync -r {{remote_host}}:{{path/to/remote_directory}} {{path/to/local_directory}}`

- Transfer directory contents (but not the directory itself) from a remote to local
`rsync -r {{remote_host}}:{{path/to/remote_directory}}/ {{path/to/local_directory}}`

- Transfer a directory recursively, in archive to preserve attributes, resolving contained softlinks , and ignoring already transferred files unless newer
`rsync -rauL {{remote_host}}:{{path/to/remote_file}} {{path/to/local_directory}}`

- Transfer file over SSH and delete remote files that do not exist locally
`rsync -e ssh --delete {{remote_host}}:{{path/to/remote_file}} {{path/to/local_file}}`

- Transfer file over SSH using a different port than the default and show global progress
`rsync -e 'ssh -p {{port}}' --info=progress2 {{remote_host}}:{{path/to/remote_file}} {{path/to/local_file}}`
