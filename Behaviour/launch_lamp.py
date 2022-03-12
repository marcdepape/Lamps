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

# alsa mixer ---------------------------------------------------------------
mixer = alsaaudio.Mixer()
mixer.setvolume(0)

# states ---------------------------------------------------------
is_broadcasting = True
is_listening = False
lamp_stream = 0
lamp_id = int(this_lamp)

if lamp_id == 0:
    is_broadcasting = True
    is_listening = False
    lamp_stream = 1
    print("LAMP " + lamp_id + " IS BROADCASTING TO " + lamp_stream)
elif lamp_id == 1:
    is_broadcasting = False
    is_listening = True
    lamp_stream = 0
    print("LAMP " + lamp_id + " IS LISTENING TO " + lamp_stream)

# pyaudio broadcast setup --------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024

audio = pyaudio.PyAudio()

context = zmq.Context()
mic_pub = context.socket(zmq.PUB)
mic_pub.bind("tcp://*:8100")
mic_pub.set_hwm(1)

def broadcast(in_data, frame_count, time_info, status):
    mic_pub.send(in_data)
    return (None, pyaudio.paContinue)

# start Recording
mic = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=broadcast)
mic.start_stream()

# pyaudio listen setup -----------------------------------------------
speaker = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
volume = 0
this_stream = 0

streams = [
    "tcp://lamp0.local:8100",
    "tcp://lamp1.local:8100",
    "tcp://lamp2.local:8100",
    "tcp://lamp3.local:8100",
    "tcp://lamp4.local:8100",
    "tcp://lamp5.local:8100",
]

listen = context.socket(zmq.SUB)
listen.connect(streams[lamp_stream])
listen.setsockopt(zmq.SUBSCRIBE, b'')
listen.set_hwm(1)

def playback():
    while True:
        if is_listening:
            data = listen.recv(CHUNK)
            spreaker.write(data)
        else:
            pass

listening = threading.Thread(target=playback)
listening.start()

# transition functions ------------------------------------------

def fadeIn():
    while volume < 100:
        volume += 1
        mixer.setvolume(volume)
        sleep(0.5)

def fadeOut():
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

# main loop ------------------------------------------------------
try:
    if is_listening:
        fadeIn()
        print ("LISTENING")
    else:
        print ("BROADCASTING")

    while True:
        pass

except KeyboardInterrupt:
    pass

mic_pub.close()
# stop Recording
mic.stop_stream()
mic.close()
audio.terminate()
