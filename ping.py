import os
from time import sleep

ping = 0

while True:
    response = os.system("ping -c 1 lamp{}.local".format(ping))
    if response != 0:
        print("LAMP {} IS OFFLINE!".format(ping))

    ping = ping + 1
    if ping > 5:
        ping = 0

    sleep(1)
