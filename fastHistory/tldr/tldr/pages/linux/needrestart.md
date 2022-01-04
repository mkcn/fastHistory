# needrestart
> Check which daemons need to be restarted after library upgrades.
> More information: <https://github.com/liske/needrestart>.

- List outdated processes
`needrestart`

- Interactively restart services
`sudo needrestart`

- List outdated processes in verbose or quiet mode
`needrestart -{{v|q}}`

- Check if the kernel is outdated
`needrestart -k`

- Check if the CPU microcode is outdated
`needrestart -w`

- List outdated processes in batch mode
`needrestart -b`

- List outdated processed using a specific configuration file
`needrestart -c {{path/to/config}}`

- Display help
`needrestart --help`
