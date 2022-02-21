#!/bin/sh
sudo ifconfig wlan0 up
ping www.github.com -c 2
git remote update
git pull
