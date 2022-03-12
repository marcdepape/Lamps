#!/usr/bin/env python

import pyaudio
import zmq
import json
import subprocess
import sys
import alsaaudio
import threading
from time import sleep

# RPI HOSTNAME ---------------------------------------------------
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)

# VARIABLES ------------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 4096

is_broadcasting = True
is_listening = False
lamp_stream = 0
lamp_id = int(this_lamp)

audio = pyaudio.PyAudio()

context = zmq.Context()
mic_pub = context.socket(zmq.PUB)
mic_pub.bind("tcp://*:8100")

def broadcast(in_data, frame_count, time_info, status):
    if is_broadcasting:
        mic_pub.send(in_data)
        return (None, pyaudio.paContinue)
    else:
        pass

streams = [
    "tcp://lamp0.local:8100",
    "tcp://lamp1.local:8100",
    "tcp://lamp2.local:8100",
    "tcp://lamp3.local:8100",
    "tcp://lamp4.local:8100",
    "tcp://lamp5.local:8100",
]

listen = context.socket(zmq.SUB)

def playback():
    speaker = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("SPEAKER CREATED")
    print(is_listening)
    while True:
        if is_listening:
            data = listen.recv(CHUNK)
            speaker.write(data)
        else:
            pass

# setup functions

def setupBroadcast():
    mic = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=broadcast)
    mic.start_stream()

def setupListen():
    listen.connect(streams[lamp_stream])
    listen.setsockopt(zmq.SUBSCRIBE, b'')
    print("ZMQ CONNECT TO: " + streams[lamp_stream])
    listening = threading.Thread(target=playback())
    print("PLAYBACK")
    listening.start()
    print("LISTENING THREAD")
# transition functions ------------------------------------------

def fadeIn(current_volume):
    while current_volume > 0:
        current_volume -= 1
        print(current_volume)
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "1%+"])
        sleep(0.5)
    return current_volume

def fadeOut(current_volume):
    while current_volume > 0:
        current_volume -= 1
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "1%-"])
        sleep(0.5)
    return current_volume

# main loop ------------------------------------------------------
try:
    volume = 0
    if lamp_id == 0:
        is_broadcasting = True
        is_listening = False
        lamp_stream = 1
        setupBroadcast()
        print("LAMP " + str(lamp_id) + " IS BROADCASTING TO " + str(lamp_stream))
    elif lamp_id == 1:
        is_broadcasting = False
        is_listening = True
        lamp_stream = 0
        setupListen()
        print("LAMP " + str(lamp_id) + " IS LISTENING TO " + str(lamp_stream))

    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "0%"])

    if is_listening:
        volume = fadeIn(volume)
        print ("LISTENING")
    else:
        print ("BROADCASTING")

    while True:
        pass

except KeyboardInterrupt:
    pass

mic_pub.close()
# stop Recording
#mic.stop_stream()
#mic.close()
audio.terminate()
