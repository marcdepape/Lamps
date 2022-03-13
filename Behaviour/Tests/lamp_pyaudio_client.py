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

def listener(in_data, frame_count, time_info, status):
    data = s.recv(CHUNK)
    return(data, pyaudio.paContinue)

stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True,
                            frames_per_buffer=CHUNK,
                            stream_callback=listener)

volume = 0
id = 1

try:
    while True:
        print("SWITCH TO: " + str(id))
        s.connect((streams[id], 8100))
        sleep(1)
        stream.start_stream()
        print(streams[id])
        sleep(15)
        id = id + 1
        if id > 5:
            id = 1
        stream.stop_stream()
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sleep(1)

except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
