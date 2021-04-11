# pngcheck
> Print detailed information about and verify PNG, JNG, and MNG files.
> More information: <http://www.libpng.org/pub/png/apps/pngcheck.html>.

- Print a summary for an image (width, height, and color depth)
`pngcheck {{image.png}}`

- Print information for an image with colorized output
`pngcheck -c {{image.png}}`

- Print verbose information for an image
`pngcheck -cvt {{image.png}}`

- Receive an image from stdin and display detailed information
`cat {{path/to/image.png}} | pngcheck -cvt`

- search for PNGs within a specific file and display information about them
`pngcheck -s {{image.png}}`

- Search for PNGs within another file and extract them
`pngcheck -x {{image.png}}`
