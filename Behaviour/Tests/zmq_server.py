#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

from time import sleep
import zmq
import json
import threading

context = zmq.Context()

# SUB
frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

# PUB
backend = context.socket(zmq.PUB)
backend.bind("tcp://*:8100")
backend.set_hwm(1)

# SUBSCRIBE TO ALL
frontend.setsockopt(zmq.SUBSCRIBE, b'')
frontend.set_hwm(1)

lamp = True

def subscribe():
    while True:
        message = frontend.recv_json()
        message = json.loads(message)
        print("NEW MESSAGE: " + message)
        sleep(1)

proxy = threading.Thread(target=subscribe)
proxy.start()

while True:
    message = json.dumps({"lamp": lamp})
    backend.send_json(message)
    lamp = not lamp
    print("DUMP: " + message)
    sleep(5)
