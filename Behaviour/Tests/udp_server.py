
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
    CHUNK = 10*1024

    #wf = wave.open("Behaviour/Tests/modular.wav")
    p = pyaudio.PyAudio()
    #print('server listening at',(host_ip, (port)),wf.getframerate())

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    #data = None
    #sample_rate = wf.getframerate()
    while True:
        msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('GOT connection from ',client_addr,msg)

        while True:
            data = stream.read(CHUNK)
            server_socket.sendto(data,client_addr)
            time.sleep(0.8*CHUNK/RATE)




t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()
