#!/usr/bin/python3
import pyaudio
import zmq
import json
import subprocess
import alsaaudio
from threading import Thread
from time import sleep

class Broadcaster(object):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    context = zmq.Context.instance()

    mic_pub = context.socket(zmq.PUB)

    def __init__(self):
        self.broadcast = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=microphone)
        self.is_broadcasting = False
        mic_pub.bind("tcp://*:8100")

    def microphone(in_data, frame_count, time_info, status):
        if self.is_broadcasting:
            mic_pub.send(in_data)
        return (None, pyaudio.paContinue)

    def start():
        self.broadcast.start_stream()

    def stop():
        self.broadcast.stop_stream()
        self.broadcast.close()
