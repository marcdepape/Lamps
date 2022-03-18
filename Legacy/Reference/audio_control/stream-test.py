#!/usr/bin/python3

import lamps
import time

stream = lamps.LampAudioStream()

for x in range(0,5):

    stream.start('lamp4.local')
    print ("listening to lamp1")
    time.sleep(2)

    stream.volume = 0.5
    time.sleep(10)
    stream.stop

    stream.start('lamp2.local')
    print ("listening to lamp2")
    time.sleep(2)

    stream.volume = 1.5
    time.sleep(10)
    stream.stop

    stream.start('lamp3.local')
    print ("listening to lamp3")
    time.sleep(2)

    stream.volume = 1.0
    time.sleep(10)
    stream.stop

stream.stop()
time.sleep(2)
