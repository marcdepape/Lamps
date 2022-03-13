#!/usr/bin/env python

import pyaudio
import socket
import sys
import alsaaudio
from time import sleep
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

mixer = alsaaudio.Mixer()
mixer.setvolume(100)

is_streaming = False

streams = [
    '192.168.100.193',
    '192.168.100.119',
    '192.168.100.162',
    '192.168.100.189',
    '192.168.100.186',
    '192.168.100.117',
]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

volume = 0
id = 1

def streaming():
    while is_streaming:
        data = s.recv(CHUNK)
        stream.write(data)

try:
    s.connect((streams[id], 8100))
    sleep(1)
    is_streaming = True
    print(streams[id])

    audio = threading.Thread(target=streaming)
    audio.start()

    while True:
        sleep(15)
        s.shutdown(2)
        s.close()
        is_streaming = False
        id = id + 1
        if id > 5:
            id = 1

        s.connect((streams[id], 8100))
        sleep(1)
        is_streaming = True
        print(streams[id])


except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
