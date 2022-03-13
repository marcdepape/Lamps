
# This is server code to send video and audio frames over UDP

import socket
import threading, wave, pyaudio, time

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 8100
# For details visit: www.pyshine.com

def audio_stream_UDP():
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

    server_socket.bind(('', 8100))

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050
    CHUNK = 8*1024

    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        server_socket.send(in_data)
        return (None, pyaudio.paContinue)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    while True:
        serversocket.accept()

t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()
