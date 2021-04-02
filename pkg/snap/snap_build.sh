#!/bin/bash

DIR_MNT=$HOME/fastHistory_snap/
mkdir -p  $DIR_MNT

# clean
rm -f -r fastHistory
rm -f  *.snap
rm -f setup.py 
rm -f README.md
mountpoint -q $DIR_MNT && fusermount -u $DIR_MNT

# get setup.py from pip folder
cp ../pip/pip_setup.py setup.py
cp ../../README.md README.md

# get fastHistory code
cp -r ../../fastHistory/ fastHistory/
rm -r fastHistory/__pycache__
rm -r fastHistory/*/__pycache__

# build snap
sudo snapcraft --use-lxd --debug --shell-after 

# check snap content
#sudo mount -t squashfs -o ro *.snap $DIR_MNT