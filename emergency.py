#!/usr/bin/env python
import random
import os

number_of_lamps = 6

for i in range(number_of_lamps):
    command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no killall 9 python3".format(i)
    os.system(command)
