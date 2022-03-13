#!/usr/bin/python3

import pyaudio
import zmq
import json
import subprocess
import alsaaudio
from threading import Thread
from time import sleep

class Lamp(object):

    def __init__(self):
        self.is_live = True
        self.is_broadcasting = True
        self.is_listening = False
        self.volume = 0
        self.id = 0
        self.stream = 0
        self.audio = None
        self.listen = None
        self.broadcast = None

lamp = Lamp()

# RPI HOSTNAME ---------------------------------------------------
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp.id = int(this_lamp)

mixer = alsaaudio.Mixer()
mixer.setvolume(0)

# VARIABLES ------------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024

audio = pyaudio.PyAudio()
context = zmq.Context.instance()

# broadcasting --------------------------------------------------------------------

mic_pub = context.socket(zmq.PUB)
mic_pub.bind("tcp://*:8100")

def broadcaster(in_data, frame_count, time_info, status):
    if lamp.is_broadcasting:
        mic_pub.send(in_data)
    return (None, pyaudio.paContinue)

lamp.broadcast = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=broadcaster)

# listening ---------------------------------------------------------------------

streams = [
    "tcp://lamp0.local:8100",
    "tcp://lamp1.local:8100",
    "tcp://lamp2.local:8100",
    "tcp://lamp3.local:8100",
    "tcp://lamp4.local:8100",
    "tcp://lamp5.local:8100",
]

speaker_sub = context.socket(zmq.SUB)

def listener(in_data, frame_count, time_info, status):
    if lamp.is_listening:
        data = speaker_sub.recv(CHUNK)
        return(data, pyaudio.paContinue)
    else:
        return(None, pyaudio.paContinue)

lamp.listen = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=listener)


# transition functions ------------------------------------------

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

# setup functions ------------------------------------------------------------

def setupBroadcast():
    fadeOut()

def setupListen():
    fadeOut()

    print("SUBSCRIBE")
    speaker_sub.connect(streams[lamp.stream])
    speaker_sub.setsockopt(zmq.SUBSCRIBE, b'')
    print("ZMQ CONNECT TO: " + streams[lamp.stream])

    print("OPEN LISTEN!!!!!")
    lamp.listen.start_stream()
    fadeIn()
    print("STREAM STARTED!!!")

# switching ------------------------------------------------------

def switcher():
    if lamp.is_broadcasting:
        lamp.is_broadcasting = False
    else:
        print("LAMP " + str(lamp.id) + " IS BROADCASTING TO " + str(lamp.stream))
        lamp.is_broadcasting = True
        setupBroadcast()

    if lamp.is_listening:
        lamp.is_listening = False
    else:
        print("LAMP " + str(lamp.id) + " IS LISTENING TO " + str(lamp.stream))
        lamp.is_listening = True
        setupListen()

if __name__ == "__main__":
    print("")
    print("--------------------------------------------")
    print("MAIN")
    print("")

    lamp.broadcast.start_stream()
    lamp.listen.start_stream()

    if lamp.id == 1:
        lamp.is_broadcasting = True
        lamp.is_listening = False
        lamp.stream = 0
        print("LAMP " + str(lamp.id) + " IS BROADCASTING TO " + str(lamp.stream))
        setupBroadcast()
    elif lamp.id == 0:
        lamp.is_broadcasting = False
        lamp.is_listening = True
        lamp.stream = 1
        print("LAMP " + str(lamp.id) + " IS LISTENING TO " + str(lamp.stream))
        setupListen()

    if lamp.is_listening:
        print("LISTENING")
    else:
        print ("BROADCASTING")

    while True:
        pass
        #sleep(30)
        #print("SWITCH!")
        #switcher()
