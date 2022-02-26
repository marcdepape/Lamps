#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

from time import sleep
import zmq
import json
import threading



# SUB
frontend_context = zmq.Context()
frontend = frontend_context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

# PUB
backend_context = zmq.Context()
backend = backend_context.socket(zmq.PUB)
backend.bind("tcp://*:8100")
backend.set_hwm(1)

# SUBSCRIBE TO ALL
frontend.setsockopt(zmq.SUBSCRIBE, b'')
frontend.set_hwm(1)

lamp = 0

def publish():
    message = json.dumps({"lamp": lamp})
    backend.send_json(message)
    lamp != lamp
    sleep(20)

proxy = threading.Thread(target=publish)
proxy.start()

while True:
    #  Wait for next request from client
    message = frontend.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)
