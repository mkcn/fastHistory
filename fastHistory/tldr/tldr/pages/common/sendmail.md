# sendmail
> Send email from the command-line.
> More information: <https://manned.org/sendmail>.

- Send a message with the content of `message.txt` to the mail directory of local user `username`
`sendmail {{username}} < {{message.txt}}`

- Send an email from you@yourdomain.com (assuming the mail server is configured for this) to test@gmail.com containing the message in `message.txt`
`sendmail -f {{you@yourdomain.com}} {{test@gmail.com}} < {{message.txt}}`

- Send an email from you@yourdomain.com (assuming the mail server is configured for this) to test@gmail.com containing the file `file.zip`
`sendmail -f {{you@yourdomain.com}} {{test@gmail.com}} < {{file.zip}}`
