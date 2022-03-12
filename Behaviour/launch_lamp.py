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
    print("LAMP " + str(lamp_id) + " IS BROADCASTING TO " + str(lamp_stream))
elif lamp_id == 1:
    is_broadcasting = False
    is_listening = True
    lamp_stream = 0
    print("LAMP " + str(lamp_id) + " IS LISTENING TO " + str(lamp_stream))

# pyaudio broadcast setup --------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024

audio_out = pyaudio.PyAudio()

context = zmq.Context()
mic_pub = context.socket(zmq.PUB)
mic_pub.bind("tcp://*:8100")

def broadcast(in_data, frame_count, time_info, status):
    if is_broadcasting:
        mic_pub.send(in_data)
        return (None, pyaudio.paContinue)
    else:
        pass

mic = audio_out.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=broadcast)

# pyaudio listen setup -----------------------------------------------
audio_in = pyaudio.PyAudio()
speaker = audio_in.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
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

def playback():
    while True:
        if is_listening:
            data = listen.recv(CHUNK)
            speaker.write(data)
        else:
            pass

listening = threading.Thread(target=playback)
listening.start()

# transition functions ------------------------------------------

def fadeIn(current_volume):
    while current_volume < 100:
        current_volume += 1
        mixer.setvolume(current_volume)
        print(current_volume)
        sleep(0.5)
    return current_volume

def fadeOut(current_volume):
    while current_volume > 0:
        current_volume -= 1
        mixer.setvolume(current_volume)
        sleep(0.5)
    return current_volume

# main loop ------------------------------------------------------
try:
    volume = 0
    if is_listening:
        mixer.setvolume(100)
        print ("LISTENING")
    else:
        mic.start_stream()
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
