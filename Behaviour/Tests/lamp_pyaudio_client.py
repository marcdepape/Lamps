#!/usr/bin/env python

import pyaudio
import socket
import sys
import alsaaudio
from time import sleep

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

mixer = alsaaudio.Mixer()
mixer.setvolume(0)
sleep(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.68.66', 8100))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

volume = 0

try:
    sleep(1)
    while volume < 100:
        volume += 1
        mixer.setvolume(volume)
        sleep(0.01)
    while True:
        data = s.recv(CHUNK)
        stream.write(data)
except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.01)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
