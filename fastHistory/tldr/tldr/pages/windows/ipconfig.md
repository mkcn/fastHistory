# ipconfig
> Display and manage the network configuration of Windows.
> More information: <https://docs.microsoft.com/windows-server/administration/windows-commands/ipconfig>.

- Show a list of network adapters
`ipconfig`

- Show a detailed list of network adapters
`ipconfig /all`

- Renew the IP addresses for a network adapter
`ipconfig /renew {{adapter}}`

- Free up the IP addresses for a network adapter
`ipconfig /release {{adapter}}`

- Remove all data from the DNS cache
`ipconfig /flushdns`
