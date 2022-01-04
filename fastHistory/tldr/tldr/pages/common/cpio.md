# cpio
> Copies files in and out of archives.
> Supports the following archive formats: cpio's custom binary, old ASCII, new ASCII, crc, HPUX binary, HPUX old ASCII, old tar, and POSIX.1 tar.
> More information: <https://www.gnu.org/software/cpio>.

- Take a list of file names from standard input and add them onto an archive in cpio's binary format
`echo "{{file1}} {{file2}} {{file3}}" | cpio -o > {{archive.cpio}}`

- Copy all files and directories in a directory and add them onto an archive, in verbose mode
`find {{path/to/directory}} | cpio -ov > {{archive.cpio}}`

- Pick all files from an archive, generating directories where needed, in verbose mode
`cpio -idv < {{archive.cpio}}`
