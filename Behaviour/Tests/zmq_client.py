#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

from time import sleep
import zmq
import json
import subprocess
import threading

# RPI HOSTNAME
this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.replace("lamp","",1)

# SERVER
server_context = zmq.Context()
server = server_context.socket(zmq.PUB)
server.connect("tcp://armadillo.local:8101")
#server.connect("tcp://bison.local:8101")
server.set_hwm(1)

# CLIENT
client_context = zmq.Context()
client = client_context.socket(zmq.SUB)
client.connect("tcp://armadillo.local:8100")
#client.connect("tcp://bison.local:8100")
client.setsockopt(zmq.SUBSCRIBE, b'')
client.set_hwm(1)

def publish():
    message = json.dumps({"lamp": this_lamp})
    server.send_json(message)
    sleep(10)

node = threading.Thread(target=publish)
node.start()

while True:
    #  Wait for next request from client
    message = client.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)
