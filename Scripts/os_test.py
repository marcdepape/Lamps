#!/usr/bin/env python
import os

command = "cd ~ ; echo marcdepape | sudo -S ./launch_broadcast.sh"
os.system(command)
#os.system("echo marcdepape | sudo -S ; sudo ./launch_broadcast.sh &")
#os.system("sudo python3 Projects/Lamps/Scripts/launch_server.py &")
