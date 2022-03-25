#!/usr/bin/env python
import zmq
import json
from time import sleep
from threading import Thread

class LampProxy(object):
    def __init__(self, num):
        #SUB PUB
        context = zmq.Context()

        self.number_of_lamps = num

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
        self.command = []
        self.listeners = []

        for i in range(self.number_of_lamps):
            self.command.append(-1)
            self.listeners.append(-1)
        self.receive = json.dumps({"id": "ID", "live": "LIVE", "fade": "FADE", "server": "SERVER", "stream": "STREAM", "state": "STATE", "console": "CONSOLE"})
        self.live = 0
        self.message = json.dumps({"rate": self.rate, "peak": self.peak, "live": -1, "command": -1, "stream": -1})

    def stop(self):
        self.running = False

    def start(self):
        #self.setup()
        self.running = True

    def statusIn(self):
        while self.running:
            self.receive = self.frontend.recv_json()
            self.receive = json.loads(self.receive)

    def updateOut(self):
        while self.running:
            for lamp_id in range(self.number_of_lamps):
                self.message = json.dumps({"lamp": lamp_id, "rate": self.rate, "peak": self.peak, "live": self.live, "command": self.command[lamp_id], "stream": self.listeners[lamp_id]})
                self.backend.send_json(self.message)
            sleep(1)

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
