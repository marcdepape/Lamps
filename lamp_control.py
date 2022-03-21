# SUB + PUB setup
import zmq
import json
from time import sleep

class LampProxy(object):
    def __init__(self, number_of_lamps):
        #SUB PUB
        context = zmq.Context()

        # SUB
        self.frontend = context.socket(zmq.SUB)
        self.frontend.bind("tcp://*:8101")

        # PUB
        self.backend = context.socket(zmq.PUB)
        self.backend.bind("tcp://*:8102")
        self.backend.set_hwm(1)

        # SUBSCRIBE TO ALL
        self.frontend.setsockopt(zmq.SUBSCRIBE, b'')
        self.frontend.set_hwm(1)

        # control variables
        self.running = False

        # MESSAGE KEYS
        self.rate = 0.05
        self.peak = 1.5
        self.state = []
        self.listeners = []

        for i in range(number_of_lamps):
            self.state.append(-1)
            self.listeners.append(-1)
        self.receive = ""
        self.live = 0
        self.message = json.dumps({"rate": self.rate, "peak": self.peak, "live": -1, "listen": -1})

    def stop(self):
        self.running = False

    def start(self):
        #self.setup()
        self.running = True
        while self.running:
            self.receive = self.frontend.recv_json()
            self.receive = json.loads(self.receive)
            print("RECEIVE: " + str(self.receive))

            lamp_id = 2
            self.message = json.dumps({"lamp": lamp_id, "rate": self.rate, "peak": self.peak, "live": self.live, "state": self.state[lamp_id], "listen": self.listeners[lamp_id]})
            self.backend.send_json(self.message)
            print("SEND: " + str(self.message))

    def setup(self):
        while self.live != 1:
            self.receive = self.frontend.recv_json()
            self.receive = json.loads(self.receive)
            self.lamp_ip[self.receive["lamp"]] = self.receive["ip"]

            num = 0
            for l in range(0,len(self.lamp_ip)):
                if self.lamp_ip[l] == -1:
                    num = num
                else:
                    num = num + 1

            if num == len(self.lamp_ip):
                self.live = 1
                self.running = True

proxy = LampProxy(6)
proxy.start()
