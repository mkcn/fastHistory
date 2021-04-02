sudo snap install fasthistory_*_amd64.snap --devmode --dangerous

snap connect fasthistory:accessrc
snap connect fasthistory:x11 :x11
snap connect fasthistory:account-control :account-control
snap connect fasthistory:home :home
