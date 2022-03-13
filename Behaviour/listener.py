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

    def speaker(in_data, frame_count, time_info, status):
        if self.is_listening:
            data = speaker_sub.recv(CHUNK)
            return(data, pyaudio.paContinue)
        else:
            return(None, pyaudio.paContinue)
            
    listen = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=speaker)

    context = zmq.Context.instance()

    streams = [
        "tcp://lamp0.local:8100",
        "tcp://lamp1.local:8100",
        "tcp://lamp2.local:8100",
        "tcp://lamp3.local:8100",
        "tcp://lamp4.local:8100",
        "tcp://lamp5.local:8100",
    ]

    speaker_sub = context.socket(zmq.SUB)

    def __init__(self):
        self.is_listening = False

    def connect(lamp_stream):
        speaker_sub.connect(streams[lamp_stream])
        speaker_sub.setsockopt(zmq.SUBSCRIBE, b'')

    def start():
        listen.start_stream()

    def stop():
        listen.stop_stream()
        listen.close()
