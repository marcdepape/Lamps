#!/usr/bin/env python
import os

number_of_lamps = 6

for i in range(number_of_lamps):
    command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo reboot now".format(i)
    os.system(command)
