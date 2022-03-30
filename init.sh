#!/bin/sh
echo Launching lamp processes!
python3 /home/pi/Projects/Lamps/launch_level.py &
python3 /home/pi/Projects/Lamps/launch_rtsp.py &
