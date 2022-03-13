#!/usr/bin/python3
import pyaudio
import zmq
import json
import subprocess
import alsaaudio
from threading import Thread
from time import sleep

class Listener(object):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050
    CHUNK = 1024

    audio = pyaudio.PyAudio()

    context = zmq.Context()
    speaker_sub = context.socket(zmq.SUB)

    streams = [
        "tcp://lamp0.local:8100",
        "tcp://lamp1.local:8100",
        "tcp://lamp2.local:8100",
        "tcp://lamp3.local:8100",
        "tcp://lamp4.local:8100",
        "tcp://lamp5.local:8100",
    ]

    def __init__(self):
        self.is_listening = False

    def speaker(in_data, frame_count, time_info, status):
            data = speaker_sub.recv(CHUNK)
            return(data, pyaudio.paContinue)

    listen = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=speaker)

    def connect(lamp_stream):
        speaker_sub.connect(streams[lamp_stream])
        speaker_sub.setsockopt(zmq.SUBSCRIBE, b'')

    def start():
        listen.start_stream()

    def stop():
        listen.stop_stream()
        listen.close()
