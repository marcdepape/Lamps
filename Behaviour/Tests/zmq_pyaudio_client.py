#!/usr/bin/env python

import pyaudio
import socket
import sys
import alsaaudio
from time import sleep
import threading
import zmq

context = zmq.Context()

#  Socket to talk to server
zmq_socket = context.socket(zmq.SUB)
zmq_socket.connect("tcp://192.168.68.66:8100")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

mixer = alsaaudio.Mixer()
mixer.setvolume(0)

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('192.168.68.66', 8100))

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

volume = 0

def streaming():
    while True:
        data = zmq_socket.recv(CHUNK)
        stream.write(data)

try:
    audio = threading.Thread(target=streaming)
    audio.start()

    while volume < 100:
        volume += 1
        mixer.setvolume(volume)
        sleep(0.5)

    while True:
        pass

except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
