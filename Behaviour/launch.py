#!/usr/bin/python3
import pyaudio
import zmq
import json
import subprocess
import alsaaudio
from threading import Thread
from time import sleep
from listener import Listener
from broadcaster import Broadcaster

class Lamp(object):
    def __init__(self):
        self.is_live = True
        self.is_broadcasting = True
        self.is_listening = False
        self.volume = 0
        self.id = 0
        self.stream = 0

lamp = Lamp()

# RPI HOSTNAME ---------------------------------------------------
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp.id = int(this_lamp)

mixer = alsaaudio.Mixer()
mixer.setvolume(0)

listener = Listener()
broadcaster = Broadcaster()

def fadeIn():
    print("FADE IN")
    volume = mixer.getvolume()
    volume = int(volume[0])
    while volume < 100:
        volume += 2
        mixer.setvolume(volume)
        sleep(0.01)
    print("VOLUME IS 100")

def fadeOut():
    print("FADE OUT")
    volume = mixer.getvolume()
    volume = int(volume[0])
    while volume > 0:
        volume -= 2
        mixer.setvolume(volume)
        sleep(0.01)
    print("VOLUME IS 0")

def setupBroadcast():
    fadeOut()
    listener.is_listening = False
    broadcaster.is_broadcasting = True

def setupListen():
    listener.is_listening = True
    broadcaster.is_broadcasting = False
    fadeIn()

if __name__ == "__main__":
    print("")
    print("--------------------------------------------")
    print("MAIN")
    print("")

    if lamp.id == 0:
        lamp.is_broadcasting = True
        lamp.is_listening = False
        lamp.stream = 1
        print("LAMP " + str(lamp.id) + " IS BROADCASTING TO " + str(lamp.stream))
    elif lamp.id == 1:
        lamp.is_broadcasting = False
        lamp.is_listening = True
        lamp.stream = 0
        print("LAMP " + str(lamp.id) + " IS LISTENING TO " + str(lamp.stream))

    if lamp.is_broadcasting:
        setupBroadcast()
    else:
        setupListen()

    listener.connect(lamp.stream)
    listener.start()
    broadcaster.start()

    while True:
        sleep(30)
        print("LOOP!")
