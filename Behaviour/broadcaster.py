#!/usr/bin/python3
import pyaudio
import zmq
import json
import subprocess
import alsaaudio
from threading import Thread
from time import sleep

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024

context = zmq.Context()
mic_pub = context.socket(zmq.PUB)

audio = pyaudio.PyAudio()

broadcasting = False

def microphone(in_data, frame_count, time_info, status):
    if broadcasting:
        mic_pub.send(in_data)
    return (None, pyaudio.paContinue)

broadcast = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=microphone)

class Broadcaster(object):
    def __init__(self):
        self.is_broadcasting = False
        mic_pub.bind("tcp://*:8100")

    def start(self):
        broadcasting = self.is_broadcasting
        broadcast.start_stream()

    def stop(self):
        broadcast.stop_stream()
        broadcast.close()
