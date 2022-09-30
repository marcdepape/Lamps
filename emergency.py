#!/usr/bin/env python
import random
import os
from time import sleep, process_time, time, strftime

for i in range(number_of_lamps):
    command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no killall -9 python".format(i)
    os.system(command)
