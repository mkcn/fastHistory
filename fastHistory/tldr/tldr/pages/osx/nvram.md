# nvram
> Manipulate firmware variables.
> More information: <https://ss64.com/osx/nvram.html>.

- print all the variables stored in the NVRAM
`nvram -p`

- print all the variables stored in the NVRAM using xML format
`nvram -xp`

- Modify the value of a firmware variable
`sudo nvram {{name}}="{{value}}"`

- delete a firmware variable
`sudo nvram -d {{name}}`

- clear all the firmware variables
`sudo nvram -c`

- Set a firmware variable from a specific xML file
`sudo nvram -xf {{path/to/file.xml}}`
