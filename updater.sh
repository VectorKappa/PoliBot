#!/bin/sh
cd /home/user/PoliBot
git pull
killall Python
killall python
apt-get upgrade
python ./main.py
exit 0