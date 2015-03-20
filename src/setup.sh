#! /bin/bash

source ~/.bash_profile
./pg_init.sh

cd ~/grano
python setup.py develop

createdb grano
grano db upgrade head