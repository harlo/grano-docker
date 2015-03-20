#! /bin/bash

source ~/.bash_profile
sudo service ssh start
sudo /etc/init.d/postgresql start

which grano
if ([ $? -eq 0 ]); then
	./setup.sh
fi

tail -f /dev/null