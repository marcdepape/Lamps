#!/usr/bin/env python

import pyaudio
import zmq
import json
import subprocess
import threading
from time import sleep

# RPI HOSTNAME
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER:" + this_lamp)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024

audio = pyaudio.PyAudio()

context = zmq.Context()
mic_stream = context.socket(zmq.PUB)
mic_stream.bind("tcp://*:8100")
mic_stream.set_hwm(1)

def callback(in_data, frame_count, time_info, status):
    mic_stream.send(in_data)
    return (None, pyaudio.paContinue)

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
stream.start_stream()

try:
    print ("STREAMING")
    while True:
        pass

except KeyboardInterrupt:
    pass

mic_stream.close()
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
