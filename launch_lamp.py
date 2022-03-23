#!/usr/bin/env python
import zmq
import json
from threading import Thread
from time import sleep
import subprocess
import board
import neopixel

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

Gst.init(None)

'''
gst-launch-1.0 rtspsrc latency=1024 location=rtsp://lamp2.local:8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
'''

class Lamp(object):
    def __init__(self, lamp_num):
        self.live = False
        self.volume = 0
        self.peak = 1.5
        self.rate = 0.05
        self.id = lamp_num
        self.stream = -1
        self.server = True
        self.change = False
        self.fade = "in"
        self.state = "?"
        self.in_update = ""
        self.out_status = ""
        self.report = True
        self.mic_signal = 0.0

        # NeoPixel
        self.pixel_pin = board.D12
        self.num_pixels = 40
        self.neo = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
        )

        # SERVER
        server_context = zmq.Context()
        self.publish = server_context.socket(zmq.PUB)
        self.publish.connect("tcp://armadillo.local:8101")
        self.publish.set_hwm(1)

        # CLIENT
        client_context = zmq.Context()
        self.subscribe = client_context.socket(zmq.SUB)
        self.subscribe.connect("tcp://armadillo.local:8102")
        self.subscribe.setsockopt(zmq.SUBSCRIBE, b'')
        self.subscribe.set_hwm(1)

        # CLIENT
        local_context = zmq.Context()
        self.levels = local_context.socket(zmq.SUB)
        self.levels.connect("tcp://localhost:8103")
        self.levels.setsockopt(zmq.SUBSCRIBE, b'')
        self.levels.set_hwm(1)

    def compare(self):
        if self.in_update["live"] != self.live:
            pass

        if self.in_update["rate"] != self.rate:
            self.rate = self.in_update["fade"]

        if self.in_update["peak"] != self.peak:
            self.peak = self.in_update["peak"]

        if self.in_update["stream"] != self.stream:
            self.stream = self.in_update["stream"]
            self.change = True
            if self.stream == -1:
                self.state = "broadcasting"
            else:
                self.state = "streaming"

    def statusOut(self):
        while self.report:
            self.out_status = json.dumps({"id": self.id, "live": self.live, "fade": self.fade, "server": self.server, "stream": self.stream, "state": self.state})
            self.publish.send_json(self.out_status)
            sleep(1)

    def updateIn(self):
        while self.report:
            update = self.subscribe.recv_json()
            update = json.loads(update)
            if update["lamp"] == self.id:
                self.in_update = update
                self.compare()
                print("RECEIVE: " + str(update))

    def micLevels(self):
        while self.report:
            self.mic_signal = self.levels.recv_string()
            print("MIC: " + str(self.mic_signal))
            self.pulse(self.mic_signal)

    def pulse(self, value):
        value = 100 + float(value)
        value = self.constrain(value, 40, 80)
        value = map_range(value, 40, 80, 0, 255)
        for i in range(num_pixels):
            self.neo[i] = (value,value,value);
            neo.show()

    def map_range(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

class Streamer(object):
    def __init__(self):
        self.AMP_ELEMENT_NAME = 'lamp-audio-amplify'
        self.RTSP_ELEMENT_NAME = 'lamp-rtsp-source'
        self.pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        self.volume = 0

        print("pipeline:", self.pipeline_string)

    def change(self, lamp_num):
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline_string = self.pipeline_template()
        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        url = "rtsp://lamp{}.local:8100/mic".format(lamp_num)
        print(url)
        self.rtspsrc.set_property('location', url)
        self.audioamplify.set_property('amplification', 0)
        self.pipeline.set_state(Gst.State.PLAYING)

    def changeVolume(self, change):
        self.volume = self.volume + change
        self.audioamplify.set_property('amplification', self.volume)

    def pipeline_template(self):
        return ("rtspsrc latency=500 name={} ! "
                "queue ! "
                "rtpvorbisdepay ! "
                "vorbisdec ! "
                "audioamplify name={} ! "
                "audioconvert ! "
                "audio/x-raw,format=S16LE,rate=44100,channels=2 ! "
                "alsasink"
                ).format(self.RTSP_ELEMENT_NAME, self.AMP_ELEMENT_NAME)

streamer = Streamer()
lamp = Lamp(lamp_id)

def fadeIn():
    while streamer.volume < lamp.peak:
        streamer.changeVolume(0.01)
        sleep(lamp.rate)
    lamp.fade = "in"

def fadeOut():
    while streamer.volume > 0:
        streamer.changeVolume(-0.01)
        sleep(lamp.rate)
    lamp.fade = "out"

if __name__ == "__main__":
    print("")
    print("--------------------------------------------")
    print("LAUNCH LAMP")
    print("")

    publisher = Thread(target=lamp.statusOut, args=())
    publisher.start()
    subscriber = Thread(target=lamp.updateIn, args=())
    subscriber.start()
    mic = Thread(target=lamp.micLevels, args=())
    mic.start()

    while lamp.state == "?":
        pass

    while True:
        if lamp.change:
            print("SWITCH | " + lamp.state + ": " + str(lamp.stream))
            fadeOut()
            if lamp.state == "streaming":
                streamer.change(lamp.stream)
                fadeIn()
                lamp.change = False
            else:
                lamp.change = False
