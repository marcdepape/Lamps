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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.68.66', 8100))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

try:
    sleep(1)
    volume = 0;
    while volume < 90:
        volume += 5
        m.setvolume(volume)
        sleep(0.1)
    while True:
        data = s.recv(CHUNK)
        stream.write(data)
except KeyboardInterrupt:
    while volume > 0:
        volume -= 5
        m.setvolume(volume)
        sleep(0.1)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
