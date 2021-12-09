# chmod
> Change the access permissions of a file or directory.
> More information: <https://www.gnu.org/software/coreutils/chmod>.

- Give the user who owns a file the right to execute it
`chmod u+x {{file}}`

- Give the user rights to read and write to a file/directory
`chmod u+rw {{file_or_directory}}`

- Remove executable rights from the group
`chmod g-x {{file}}`

- Give all users rights to read and execute
`chmod a+rx {{file}}`

- Give others (not in the file owner's group) the same rights as the group
`chmod o=g {{file}}`

- Remove all rights from others
`chmod o= {{file}}`

- Change permissions recursively giving group and others the ability to write
`chmod -R g+w,o+w {{directory}}`

- Recursively give all users read permissions to files and eXecute permissions to sub-directories within a directory
`chmod -R a+rX {{directory}}`
