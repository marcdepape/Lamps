#!/usr/bin/env python
import random
import os

for i in range(number_of_lamps):
    command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no killall -9 python".format(i)
    os.system(command)
