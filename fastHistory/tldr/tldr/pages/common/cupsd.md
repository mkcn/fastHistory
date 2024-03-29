# cupsd
> Server daemon for the CUPS print server.
> More information: <https://www.cups.org/doc/man-cupsd.html>.

- Start `cupsd` in the background, aka. as a daemon
`cupsd`

- Start `cupsd` on the foreground
`cupsd -f`

- launch `cupsd` on-demand (commonly used by `launchd` or `systemd`)
`cupsd -l`

- Start `cupsd` using the specified [`c`]`upsd.conf` configuration file
`cupsd -c {{path/to/cupsd.conf}}`

- Start `cupsd` using the specified `cups-file`[`s`]`.conf` configuration file
`cupsd -s {{path/to/cups-files.conf}}`

- test the [`c`]`upsd.conf` configuration file for errors
`cupsd -t -c {{path/to/cupsd.conf}}`

- test the `cups-file`[`s`]`.conf` configuration file for errors
`cupsd -t -s {{path/to/cups-files.conf}}`

- Display all available options
`cupsd -h`
