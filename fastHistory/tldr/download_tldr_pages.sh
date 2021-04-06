#TODO move this script and format_tldr_pages.py to a different folder

rm -f -r pages
rm -f LICENSE.md
# download pages
git clone https://github.com/tldr-pages/tldr.git
# keep only eng version
mv tldr/pages pages
mv tldr/LICENSE.md LICENSE.md
# keep only .md files
find pages -type f ! -name '*.md' -delete
# fix pages with python
python3 fix_pages.py
# clean
rm -r tldr