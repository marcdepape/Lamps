#!/usr/bin/env python

import pyaudio
import socket
import sys
import subprocess
import alsaaudio
from time import sleep
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 16*1024

# RPI HOSTNAME ---------------------------------------------------
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

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
id = lamp_id + 1

def streaming():
    print("NOW STREAMING")
    while is_streaming:
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

    while True:
        id = id + 1
        if id > 5:
            id = 1

        if id == lamp_id:
            id = id + 1

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



except KeyboardInterrupt:
    while volume > 0:
        volume -= 1
        mixer.setvolume(volume)
        sleep(0.5)

print('Shutting down')
s.close()
stream.close()
audio.terminate()
