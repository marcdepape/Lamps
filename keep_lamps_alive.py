import os
from time import sleep

lamps = [][]
address = 0
state = 1


for i in range(6):
    lamps[i][address] = "lamp{}.local".format(i)
    lamps[i][state] = 0

lamps_live = 0

while lamps_live != 6:
    for i in range(6):
        if lamps[i][state] != True:
            response = os.system("ping -c 1 " + lamps[i][address])
            print("LAMP {}: {}".format(i, response))
            lamps[i][state] = response

    lamps_live = 0
    for i in range(6):
        lamps_live = lamps_live + lamps[i][state]

print("ALL LIVE!")

live = False

while True:
    for i in range(6):
        if lamps[i][state] != True:
            response = os.system("ping -c 1 " + lamps[i][address])
            print("LAMP {}: {}".format(i, response))
            lamps[i][state] = response

    lamps_live = 0
    for i in range(6):
        lamps_live = lamps_live + lamps[i][state]

    if lamps_live == 6 && live == False:
        print("ALL ARE LIVE!")
        live = True
    elif lamps_live < 6:
        print("OFFLINE!")

    sleep(1)





response = os.system("ping -c 1 " + hostname)

#and then check the response...
