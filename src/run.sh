#! /bin/bash

source ~/.bash_profile
sudo service ssh start
sudo /etc/init.d/postgresql start
tail -f /dev/null