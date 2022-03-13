#!/usr/bin/env python

import pyaudio
import socket
import sys
import alsaaudio
from time import sleep
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
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
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK,)

volume = 0
id = 1

def streaming():
    state = True
    while is_streaming:
        if state:
            print("NOW STREAMING")
            state = False
        data = s.recv(CHUNK)
        stream.write(data)

try:
    is_streaming = False
    s.connect((streams[id], 8100))
    sleep(1)
    is_streaming = True
    print(streams[id])

    audio = threading.Thread(target=streaming)
    audio.start()

    sleep(15)
    id = id + 1

    while True:
        print("SWITCH TO: " + str(id))
        is_streaming = False
        audio.join()
        print("THREAD CLOSED!")
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sleep(1)
        s.connect((streams[id], 8100))
        sleep(1)
        is_streaming = True
        audio = threading.Thread(target=streaming)
        audio.start()
        print(streams[id])
        sleep(15)
        id = id + 1
        if id > 5:
            id = 1


except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
