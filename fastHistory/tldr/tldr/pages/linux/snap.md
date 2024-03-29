# snap
> Tool for managing the "snap" self-contained software packages.
> Similar to what `apt` is for ".deb".

- Search for a package
`snap find {{package_name}}`

- Install a package
`snap install {{package_name}}`

- Update a package
`snap refresh {{package_name}}`

- Update a package to another channel (track, risk, or branch)
`snap refresh {{package_name}} --channel={{channel}}`

- Update all packages
`snap refresh`

- Display basic information about installed snap software
`snap list`

- Uninstall a package
`snap remove {{package_name}}`

- Check for recent snap changes in the system
`snap changes`
