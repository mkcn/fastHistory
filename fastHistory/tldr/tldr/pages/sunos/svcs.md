# svcs
> List information about running services.
> More information: <https://www.unix.com/man-page/linux/1/svcs>.

- List all running services
`svcs`

- List services that are not running
`svcs -vx`

- List information about a service
`svcs apache`

- Show location of service log file
`svcs -L apache`

- Display end of a service log file
`tail $(svcs -L apache)`
