#!/usr/bin/env python
import os

command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./pull.sh".format(0)
os.system(command)

command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo python3 /Projects/Lamps/Scripts/is_test.py".format(0)
os.system(command)
