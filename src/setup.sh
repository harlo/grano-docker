#! /bin/bash

source ~/.bash_profile
sudo /etc/init.d/postgresql start
./pg_init.sh

cd ~/grano
python setup.py develop

createdb grano
grano db upgrade head