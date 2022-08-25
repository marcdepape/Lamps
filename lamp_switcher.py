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

default = 255
stream = 0
broadcast = -1
number_of_lamps = 6

broadcast_count = []
broadcast_count = [0 for i in range(number_of_lamps)]

stream_count = []
stream_count = [0 for i in range(number_of_lamps)]

new_states = []
new_states = [default for i in range(number_of_lamps)]

previous_states = []
previous_states = [default for i in range(number_of_lamps)]

last_states = []
last_states = [default for i in range(number_of_lamps)]

def shuffleLamps():
    broadcasts = 0
    streams = 0
    broadcast_lamps = []

    old = [default for i in range(number_of_lamps)]
    for i in range(number_of_lamps):
        last_states[i] = previous_states[i]
        old[i] = new_states[i]

    for i in range(number_of_lamps):
        new_states[i] = default

    for i in range(number_of_lamps):
        if stream_count[i] == 2:
            new_states[i] = broadcast
            stream_count[i] = 0
            broadcasts = broadcasts + 1
            broadcast_lamps.append(i)
            print("{} TO BROADCAST".format(i))

    for i in range(number_of_lamps):
        if broadcast_count[i] == 2:
            if broadcast_lamps:
                assignment = random.choice(broadcast_lamps)
                new_states[i] = assignment
                broadcast_lamps.remove(assignment)
                stream_count[i] = stream_count[i] + 1
                broadcast_count[i] = 0
            else:
                while new_states[i] == default:
                    assignment = random.randint(0, number_of_lamps-1)
                    if assignment != i:
                        new_states[i] = assignment
                        if new_states[assignment] != broadcast:
                            new_states[assignment] == broadcast
                            stream_count[assignment] = 0
                            broadcasts = broadcasts + 1
                            broadcast_lamps.append(assignment)
            print("{} TO STREAM".format(i))

    while broadcasts < 3:
        assignment = random.randint(0, number_of_lamps-1)

        if new_states[assignment] == default:
            new_states[assignment] = broadcast
            broadcast_lamps.append(assignment)
            broadcast_count[assignment] = broadcast_count[assignment] + 1
            broadcasts = broadcasts + 1
            stream_count[assignment] = 0

    for i in range(number_of_lamps):
        tries = 0
        duplicate = -1
        if new_states[i] == default:
            while new_states[i] == default and tries < number_of_lamps:
                assignment = random.choice(broadcast_lamps)
                if assignment != old[i]:
                    new_states[i] = assignment
                    broadcast_lamps.remove(assignment)
                    stream_count[i] = stream_count[i] + 1
                    broadcast_count[i] = 0
                else:
                    print("ALREADY STREAMING {}".format(assignment))
                    tries = tries + 1

            if tries >= number_of_lamps:
                swaping = True
                while swaping:
                    swap = random.randint(0, number_of_lamps-1)
                    if swap != i and new_states[swap] != broadcast:
                        print("SWAPING {} and {}".format(i, swap))
                        new_stream = new_states[swap]
                        new_states[swap] = new_states[i]
                        new_states[i] = new_stream
                        swaping = False


    print("NEW STATES----------------------")
    print(old)
    print(new_states)
    previous_states = new_states
    return new_states

def pull():
    for i in range(number_of_lamps):
        command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./pull.sh".format(i)
        os.system(command)

def updateStates():
    for i in range(number_of_lamps):
        if new_states[i] == broadcast:
            command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./launch_broadcast.sh &".format(i)
            message = "LAMP {} IS BROADCASTING".format(i)
            print(message)
            os.system(command)
        else:
            command = "sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./launch_stream.sh {} {} &".format(i, new_states[i], last_states[i])
            message = "LAMP {} IS STREAMING LAMP {}".format(i, new_states[i])
            print(message)
            os.system(command)

if __name__ == '__main__':
    pull()
    sleep(10)
    while True:
        print("SHUFFLE LAMPS-------------------")
        shuffleLamps()
        print("UPDATE STATES-------------------")
        updateStates()
        cycle = random.randint(15, 20)
        print("NEXT CYCLE------------------")
        print(cycle)
        sleep(cycle)
