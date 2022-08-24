#!/usr/bin/env python
import random
import os
from time import sleep, process_time, time, strftime

#ssh-keygen -R 192.

# launch_broadcast.sh script
'''
#!/bin/bash
sudo killall -9 python3
cd Projects/Lamps/
git reset --hard
git pull
sudo alsactl restore -f alsa_lamps_codec.state
sudo python3 Scripts/launch_server.py &
'''

'''
#!/bin/bash
sudo killall -9 python3
cd Projects/Lamps/
git reset --hard
git pull
sudo alsactl restore -f alsa_lamps_codec.state
sudo python3 Scripts/launch_stream.py --num $1 &
'''

#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch_broadcast.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch_lamp.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp2.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp3.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp4.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp5.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch_broadcast.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch_stream.sh 0 &")
#sleep(60)
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch_broadcast.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch_stream.sh 1 &")
#sleep(60)

default = 255
stream = 0
broadcast = -1
number_of_lamps = 6

broadcast_states = []
broadcast_states = [0 for i in range(number_of_lamps)]

stream_states = []
stream_states = [0 for i in range(number_of_lamps)]

new_states = []
new_states =  [default for i in range(number_of_lamps)]

def shuffleLamps()
    broadcasts = 0
    streams = 0

    new_states =  [default for i in range(number_of_lamps)]
    for i in range(number_of_lamps):
        if broadcast_states[i] == 2:
            new_states[i] == stream
            broadcast_states[i] = 0
            streams = streams + 1

        if stream_states[i] == 2:
            new_states[i] == broadcast
            stream_states[i] = 0
            broadcasts = broadcasts + 1

    while broadcasts < 3:
        assignment = random.randint(0, number_of_lamps-1)
        if new_states[assignment] == -1:
            new_states[assignment] = broadcast
            broadcast_states[assignment] = broadcast_states[assignment] + 1

    while streams < 3:
        assignment = random.randint(0, number_of_lamps-1)
        if new_states[assignment] == -1:
            new_states[assignment] = assignment
            stream_states[assignment] = stream_states[assignment] + 1

    print("NEW STATES----------------------")
    print(new_states)

def updateStates()
    for i in range(number_of_lamps):
        if new_states[i] == broadcast
            command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./launch_broadcast.sh &".format(i)
            os.system(command)
        elif new_states[i] = stream:
            command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./launch_stream.sh {} &".format(i, new_states[i])
            os.system(command)

if __name__ == '__main__':
    while True:
        shuffleLamps()
        updateStates()
        sleep(60)
