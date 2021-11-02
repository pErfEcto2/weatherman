#!/bin/bash

mkdir -p /home/projects/weatherman
cd /home/projects/weatherman
pip3 install -r requirements.txt
echo "place here bot id "
read var_bot_id
echo $var_bot_id > bot_id
echo "place here GisMeteo api token"
read api_token
echo $api_token > gismeteo_token
echo "place here your telegram nickname"
read nikename
echo $nikename > creator
echo "place here data base info (<table name> <database name> <username>)"
read dbInfo
echo $dbInfo > dbInfo
chmod 777 bot_starter.sh
chmod 777 weatherman.py
chmod 755 weatherman.service
ln -s home/projects/weatherman/weatherman.service /etc/systemd/system/weatherman.service
systemctl enable weatherman.service
systemctl start weatherman.service