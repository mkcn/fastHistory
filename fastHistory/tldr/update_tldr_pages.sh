####################################
#
# run this only to update 
#
####################################

echo "Clean"
rm -f -r tldr
echo "Download the most updated pages"
git clone https://github.com/tldr-pages/tldr.git tdlr_tmp
echo "Keep only pages folder and licence"
mkdir tldr
mv tdlr_tmp/pages tldr/pages # NOTE: to use a different language change this line (e.g. mv tldr/pages.it pages)  
mv tdlr_tmp/LICENSE.md tldr/LICENSE.md
find tldr/pages -type f ! -name '*.md' -delete

current_date=$(date +'%Y-%m-%d') 
last_commit_id=$(git ls-remote https://github.com/tldr-pages/tldr.git | grep HEAD | cut -f 1)
echo "Current date: " $current_date
echo "Last commit id: " $last_commit_id
echo $current_date > tldr/last_update_date.txt
echo $last_commit_id > tldr/last_tldr_commit.txt
echo "Call python script"
python3 -c "from tldrParser import TLDRParser; t=TLDRParser(); print(t.format_tldr_pages())"
echo "Clean"
rm -f -r tdlr_tmp
echo "Done"