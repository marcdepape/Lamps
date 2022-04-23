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
        self.running = True

        # MESSAGE KEYS
        self.fade_rate = 0.05
        self.peak = 1.5
        self.saturation = 1.0
        self.pulse_point = 65
        self.command = []
        self.listeners = []

        for i in range(self.number_of_lamps):
            self.command.append(-1)
            self.listeners.append(-1)
            self.command.append("none")

        self.receive = json.dumps({"id": -1,
                                "fade": "FADE",
                                "saturation": "SATURATION",
                                "stream": "STREAM",
                                "state": "STATE",
                                "command": "none",
                                "pulse": "PULSE"
                                "mic": 0,
                                "console": "Waiting..."})

        self.message = json.dumps({"rate": self.fade_rate,
                                "peak": self.peak,
                                "saturation": self.saturation,
                                "pulse": self.pulse_point,
                                "command": "none",
                                "stream": -1})

    def statusIn(self):
        while self.running:
            self.receive = self.frontend.recv_json()

    def updateOut(self):
        while self.running:
            for lamp_id in range(self.number_of_lamps):
                self.message = json.dumps({"lamp": lamp_id,
                                        "rate": self.fade_rate,
                                        "peak": self.peak,
                                        "saturation": self.saturation,
                                        "command": self.command[lamp_id],
                                        "stream": self.listeners[lamp_id]})
                self.backend.send_json(self.message)
            sleep(1)
