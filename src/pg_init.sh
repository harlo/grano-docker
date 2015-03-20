sudo /etc/init.d/postgresql start
sudo -u postgres psql -c "create user granotest PASSWORD 'grano'" postgres
sudo -u postgres psql -c "alter user granotest with createdb" postgres