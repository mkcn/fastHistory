# fisher
> Fisher, a fish-shell plugin manager.
> Install plugins by name or from a managed 'fishfile' for bundled installs.
> More information: <https://github.com/jorgebucaran/fisher>.

- Install one or more plugins
`fisher {{plugin1}} {{plugin2}}`

- Install a plugin from a GitHub gist
`fisher {{gist_url}}`

- Edit 'fishfile' manually with your favorite editor and install multiple plugins
`{{editor}} ~/.config/fish/fishfile; fisher`

- List installed plugins
`fisher ls`

- Update plugins
`fisher update`

- Remove one or more plugins
`fisher remove {{plugin1}} {{plugin2}}`
