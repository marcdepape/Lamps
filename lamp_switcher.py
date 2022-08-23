#!/usr/bin/env python
import random
import os
from time import sleep, process_time, time, strftime

#ssh-keygen -R 192.
os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch_broadcast.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch_lamp.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp2.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp3.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp4.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp5.local sudo ./launch.sh &")

# launch_broadcast.sh script
'''
sudo killall -9 python3
cd Projects/Lamps/
git reset --hard
git pull
sudo alsactl restore -f alsa_lamps_codec.state
sudo python3 Script/fase_out.py &
sudo python3 Scripts/launch_server.py
sudo python3 Scripts/pulse_mic.py &
'''
