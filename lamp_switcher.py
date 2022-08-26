#!/usr/bin/env python
import random
import os
from time import sleep, process_time, time, strftime

#ssh-keygen -R 192.

# launch_broadcast.sh script
'''
#!/bin/bash
cd Projects/Lamps/
sudo python3 Scripts/fade_audio_out.py
sudo killall -9 python3
sudo python3 Scripts/fade_audio_in.py
sudo python3 Scripts/launch_server.py &
'''

'''
#!/bin/bash
cd Projects/Lamps/
sudo python3 Scripts/fade_audio_out.py
sudo killall -9 python3
sudo python3 Scripts/fade_audio_in.py
sudo python3 Scripts/launch_stream.py --num $1 --state $2 &
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

last_states = []
last_states = [default for i in range(number_of_lamps)]

def shuffleLamps():
    broadcasts = 0
    streams = 0
    broadcast_lamps = []
    broadcast_check = []
    stream_lamps = []

    old = [default for i in range(number_of_lamps)]
    for i in range(number_of_lamps):
        last_states[i] = new_states[i]
        old[i] = new_states[i]

    for i in range(number_of_lamps):
        new_states[i] = default

    for i in range(number_of_lamps):
        if stream_count[i] == 2:
            new_states[i] = broadcast
            stream_count[i] = 0
            broadcasts = broadcasts + 1
            broadcast_lamps.append(i)
            broadcast_check.append(i)
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
                            broadcast_check.append(assignment)
            stream_lamps.append(i)
            print("{} TO STREAM".format(i))

    while broadcasts < 3:
        assignment = random.randint(0, number_of_lamps-1)

        if new_states[assignment] == default:
            new_states[assignment] = broadcast
            broadcast_lamps.append(assignment)
            broadcast_check.append(assignment)
            broadcast_count[assignment] = broadcast_count[assignment] + 1
            broadcasts = broadcasts + 1
            stream_count[assignment] = 0

    for i in range(number_of_lamps):
        if new_states[i] == default:
            while new_states[i] == default:
                assignment = i
                while assignment == i:
                    assignment = random.choice(broadcast_lamps)
                new_states[i] = assignment
                broadcast_lamps.remove(assignment)
                stream_count[i] = stream_count[i] + 1
                broadcast_count[i] = 0
                stream_lamps.append(i)

    print("STREAMERS--------------------")
    print(stream_lamps)

    duplicate = True
    swaps = []
    swaps = [default for i in range(3)]

    while duplicate:
            count = 0
            for i in range(3):
                if new_states[stream_lamps[i]] == old[stream_lamps[i]]:
                    count = count + 1

            if count > 0:
                for i in range(3):
                    swaps[i] = broadcast_lamps[i]

                assignment = random.choice(swaps)
                new_states[stream_lamps[0]] = assignment
                swaps.remove(assignment)

                assignment = random.choice(swaps)
                new_states[stream_lamps[1]] = assignment
                swaps.remove(assignment)

                assignment = random.choice(swaps)
                new_states[stream_lamps[2]] = assignment
                swaps.remove(assignment)

                print("SWAPING--------------------")
                print(new_states)
            else:
                duplicate = False

    print("NEW STATES----------------------")
    print(old)
    print(new_states)
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
        #cycle = random.randint(90, 180)
        cycle = 60
        print("NEXT CYCLE------------------")
        print(cycle)
        sleep(cycle)
