#!/bin/sh
echo Launching lamp processes!
sudo python3 /home/pi/Projects/Lamps/launch_lamp.py &
python3 /home/pi/Projects/Lamps/launch_level.py &
python3 /home/pi/Projects/Lamps/launch_rtsp.py &
