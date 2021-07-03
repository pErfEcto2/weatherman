#!/bin/bash

pip3 install -r requirements.txt
echo "place here bot id "
read var_bot_id
touch bot_id
echo $var_bot_id > bot_id
chmod 777 bot_starter.sh
chmod 777 weatherman.py
ln -s $PWD/weatherman.service /etc/systemd/system/weatherman.service
systemctl enable weatherman.service
systemctl start weatherman.service