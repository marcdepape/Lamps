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
socket = context.socket(zmq.REP)
zmq_socket.bind("tcp://*:5555")

def callback(in_data, frame_count, time_info, status):
    for s in read_list[1:]:
        zmq_socket.send(in_data)
    return (None, pyaudio.paContinue)

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
# stream.start_stream()

read_list = [serversocket]
print ("recording...")

try:
    while True:
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is zmq_socket:
                (zmq_socket, address) = zmq_socket.accept()
                read_list.append(zmq_socket)
                print ("Connection from", address)
            else:
                read_list.remove(s)
                print ("Client connection closed")

except KeyboardInterrupt:
    pass


print ("finished recording")

zmq_socket.close()
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
