#!/usr/bin/env python
import os
import subprocess

#command = "cd ~ ; echo marcdepape | sudo -S ./launch_broadcast.sh"
#os.system(command)
#os.system("echo marcdepape | sudo -S ; sudo ./launch_broadcast.sh &")
#os.system("sudo ./Projects/Lamps/Scripts/relaunch_server.sh")
os.system("sudo bash launch_broadcast.sh")
#subprocess.call("./launch_broadcast.sh", shell=True)
