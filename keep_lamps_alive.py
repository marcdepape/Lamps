import os
from time import sleep

print("PING ALL LAMPS!")

address = []
state = []

for i in range(6):
    address.append("lamp{}.local".format(i))
    state.append(0)

live = False

while True:
    for i in range(6):
        response = os.system("ping -c 1 " + address[i])
        print("LAMP {}: {}".format(i, response))
        if response > 0:
            state[i] = True

    lamps_live = 0
    for i in range(6):
        lamps_live = lamps_live + state[i]

    if lamps_live == 6 and live == False:
        print("ALL ARE LIVE!")
        live = True
    elif lamps_live < 6:
        print("OFFLINE!")
        live = False

    sleep(5)





response = os.system("ping -c 1 " + hostname)

#and then check the response...
