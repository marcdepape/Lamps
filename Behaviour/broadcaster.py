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

    context = zmq.Context.instance()
    mic_pub = context.socket(zmq.PUB)

    def __init__(self):
        self.is_broadcasting = False
        mic_pub.bind("tcp://*:8100")

    audio = pyaudio.PyAudio()

    def microphone(in_data, frame_count, time_info, status):
        if self.is_broadcasting:
            mic_pub.send(in_data)
        return (None, pyaudio.paContinue)

    broadcast = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=microphone)

    def start():
        broadcast.start_stream()

    def stop():
        broadcast.stop_stream()
        broadcast.close()
