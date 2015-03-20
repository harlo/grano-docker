#! /bin/bash

cd ~/grano
virtualenv env
source ~/.bash_profile

cp grano/default_settings.py $GRANO_SETTINGS
pip install -r requirements.txt