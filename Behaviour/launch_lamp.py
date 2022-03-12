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

context = zmq.Context()

# broadcasting --------------------------------------------------------------------

mic_pub = context.socket(zmq.PUB)
mic_pub.bind("tcp://*:8100")

def broadcaster(in_data, frame_count, time_info, status):
    print("INSIDE BROADCASTER")
    if lamp.is_broadcasting:
        mic_pub.send(in_data)
        return (None, pyaudio.paContinue)
    else:
        pass

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
    print("INSIDE LISTENER")
    if lamp.is_listening:
        data = speaker_sub.recv(CHUNK)
        listen.write(data)
        return(None, pyaudio.paContinue)
    else:
        pass

# transition functions ------------------------------------------

def fadeIn():
    volume = mixer.getvolume()
    volume = int(volume[0])
    while volume < 100:
        volume += 1
        mixer.setvolume(volume)
        sleep(0.5)

def fadeOut():
    volume = mixer.getvolume()
    volume = int(volume[0])
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

# setup functions ------------------------------------------------------------

def setupBroadcast():
    print("SETUP BROADCAST!!!!!")
    if lamp.listen.is_active():
        print("LISTEN OPEN")
        fadeOut()
        lamp.is_listening = False;
        lamp.listen.stop_stream()
        lamp.listen.close()
        print("LISTEN CLOSED")

    print("OPEN BROADCAST!!!!!")
    lamp.broadcast = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=broadcaster)
    lamp.broadcast.start_stream()

def setupListen():
    print("SETUP LISTEN!!!!!")
    if lamp.broadcast.is_active():
        print("BROADCAST OPEN")
        fadeOut()
        lamp.is_broadcasting = False;
        lamp.broadcast.stop_stream()
        lamp.broadcast.close()
        print("BROADCAST CLOSED")

    print("SUBSCRIBE")
    speaker_sub.connect(streams[lamp.stream])
    speaker_sub.setsockopt(zmq.SUBSCRIBE, b'')
    print("ZMQ CONNECT TO: " + streams[lamp.stream])

    print("OPEN LISTEN!!!!!")
    lamp.listen = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=listener)
    lamp.listen.start_stream()
    print("NEW STREAM")
    fadeIn()


# switching ------------------------------------------------------

def switcher():
    if lamp.is_broadcasting:
        lamp.is_broadcasting = False
    else:
        print("LAMP " + str(lamp.id) + " IS BROADCASTING TO " + str(lamp.stream))
        lamp.is_broadcasting = True
        setupBroadcast()

    if lamp.is_listening:
        is_listening = False
    else:
        print("LAMP " + str(lamp.id) + " IS LISTENING TO " + str(lamp.stream))
        lamp.is_listening = True
        setupListen()

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
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
        setupBroadcast()
    elif lamp.id == 1:
        lamp.is_broadcasting = False
        lamp.is_listening = True
        lamp.stream = 0
        print("LAMP " + str(lamp.id) + " IS LISTENING TO " + str(lamp.stream))
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "100%"])
        setupListen()

    if lamp.is_listening:
        print("LISTENING")
    else:
        print ("BROADCASTING")

    while True:
        sleep(10)
        print("SWITCH!")
        switcher()
