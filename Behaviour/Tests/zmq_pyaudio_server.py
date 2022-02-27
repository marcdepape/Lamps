#!/usr/bin/env python

import pyaudio
import socket
import select
import zmq

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

audio = pyaudio.PyAudio()

#serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#serversocket.bind(('', 8100))
#serversocket.listen(5)

context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_socket.bind("tcp://*:8100")
zmq_socket.set_hwm(1)

def callback(in_data, frame_count, time_info, status):
    zmq_socket.send(in_data)
    return (None, pyaudio.paContinue)

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
# stream.start_stream()

read_list = [zmq_socket]
print ("recording...")

try:
    while True:
        pass

except KeyboardInterrupt:
    pass


print ("finished recording")

zmq_socket.close()
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
