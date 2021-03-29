# get setup.py from pip folder
#cp ../pip/setup.py setup.py

# get fastHistory code
#cp ../../fastHistory fastHistory

# build snap
sudo snapcraft --use-lxd --shell-after --debug

# move *.snap file
