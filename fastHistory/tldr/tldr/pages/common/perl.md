# perl
> The Perl 5 language interpreter.
> More information: <https://www.perl.org>.

- Parse and execute a Perl script
`perl {{script.pl}}`

- Check syntax errors on a Perl script
`perl -c {{script.pl}}`

- Parse and execute a Perl statement
`perl -e {{perl_statement}}`

- Run a Perl script in debug mode, using `perldebug`
`perl -d {{script.pl}}`

- Loop over all lines of a file, editing them in-place using a find/replace expression
`perl -p -i -e 's/{{find}}/{{replace}}/g' {{filename}}`

- Run a find/replace expression on a file, saving the original file with a given extension
`perl -p -i'.old' -e 's/{{find}}/{{replace}}/g' {{filename}}`

- Run a multiline find/replace expression on a file, and save the result in another file
`perl -p0e 's/{{foo\nbar}}/{{foobar}}/g' {{input_file}} > {{output_file}}`

- Run a regular expression on stdin, printing out the first capture group for each line
`cat {{path/to/input_file}} | perl -nle 'if (/.*({{foo}}).*/) {print "$1"; last;}'`
