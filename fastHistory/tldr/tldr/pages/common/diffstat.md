# diffstat
> Create a histogram from the output of the `diff` command.
> More information: <https://manned.org/diffstat>.

- Display changes in a histogram
`diff {{file1}} {{file2}} | diffstat`

- Display inserted, deleted and modified changes as a table
`diff {{file1}} {{file2}} | diffstat -t`
