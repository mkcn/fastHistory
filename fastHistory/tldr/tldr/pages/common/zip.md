# zip
> Package and compress (archive) files into zip file.
> More information: <https://manned.org/zip>.

- Package and compress files and directories recursively
`zip -r {{compressed.zip}} {{path/to/file}} {{path/to/directory1}} {{path/to/directory2}}`

- Exclude unwanted files from being added to the compressed archive
`zip -r {{compressed.zip}} {{path/to/directory}} -x {{path/to/exclude}}`

- Archive a directory and its contents with the highest level 9 of compression
`zip -r -{{9}} {{compressed.zip}} {{path/to/directory}}`

- Create an encrypted archive (user will be prompted for a password)
`zip -e -r {{compressed.zip}} {{path/to/directory}}`

- Add files to an existing zip file
`zip {{compressed.zip}} {{path/to/file}}`

- Delete files from an existing zip file
`zip -d {{compressed.zip}} "{{foo/*.tmp}}"`

- Archive a directory and its contents to a multi-part split zip file (e.g. 3 GB parts)
`zip -r -s {{3g}} {{compressed.zip}} {{path/to/directory}}`

- List files within a specified archive (without extracting them)
`zip -sf {{compressed.zip}}`
