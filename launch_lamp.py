#!/usr/bin/env python
import zmq
import json
from threading import Thread
from time import sleep
import subprocess
import board
import neopixel
import os

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
        self.id = lamp_num
        self.live = False
        self.volume = 0
        self.peak = 1.5
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.stream = 255
        self.change = False
        self.changing = 0
        self.state = "?"
        self.in_update = ""
        self.out_status = ""
        self.console = "Launching..."
        self.report = True
        self.mic_signal = 0.0
        self.top_bright = 0
        self.bottom_bright = 0
        self.command = "null"

        # NeoPixel
        self.pixel_pin = board.D12
        self.num_pixels = 40
        self.neo = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB
        )
        self.setOff()

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
        if self.in_update["command"] != self.command:
            self.command = self.in_update["command"]
            if self.command == "reboot":
                self.proxy.command[self.id] = "complete"
                self.setReboot()
                print("REBOOT!")
                #os.system("reboot now")
            if self.command == "start":
                self.state = "start"
                self.proxy.command[self.id] = "complete"

        if self.in_update["rate"] != self.fade_rate:
            self.fade_rate = self.in_update["fade"]

        if self.in_update["peak"] != self.peak:
            self.peak = self.in_update["peak"]

        if self.in_update["saturation"] != self.saturation:
            self.saturation = self.in_update["saturation"]
            if self.state == "streaming":
                self.setBulb(100)

        if self.in_update["stream"] != self.stream:
            self.stream = self.in_update["stream"]
            self.change = True
            self.changing = 1
            if self.stream == -1:
                self.state = "broadcasting"
            else:
                self.state = "streaming"

    def statusOut(self):
        while self.report:
            self.out_status = json.dumps({"id": self.id,
                                        "fade": self.fade_rate,
                                        "saturation": self.saturation,
                                        "stream": self.stream,
                                        "state": self.state,
                                        "command": self.command,
                                        "console": self.console})
            self.publish.send_json(self.out_status)
            sleep(1)

    def updateIn(self):
        while self.report:
            update = self.subscribe.recv_json()
            update = json.loads(update)
            if update["lamp"] == self.id:
                self.in_update = update
                self.compare()
                print(self.in_update)

    def micLevels(self):
        while self.report:
            self.mic_signal = self.levels.recv_string()
            if self.state == "broadcasting":
                self.pulse(self.mic_signal)

    def pulse(self, rms):
        self.bottom_bright = 100 + float(rms)
        self.bottom_bright = self.constrain(self.bottom_bright, 55, 90)
        self.bottom_bright = self.mapRange(self.bottom_bright, 55, 90, 0, 255)
        self.bottom_bright = int(self.bottom_bright * self.saturation)
        self.setBase(self.bottom_bright)

    def setBase(self, value):
        self.bottom_bright = value

        if self.bottom_bright < 0:
            self.bottom_bright = 0
        if self.bottom_bright > 255:
            self.bottom_bright = 255

        intensity = int(self.bottom_bright * self.saturation)

        for i in range(16, self.num_pixels):
            self.neo[i] = (intensity,intensity,intensity);
        self.neo.show()

    def setBulb(self, value):
        value = self.mapRange(value, 0, 100, 0, 255)
        self.top_bright = self.top_bright + value

        if self.top_bright < 0:
            self.top_bright = 0
        if self.top_bright > 255:
            self.top_bright = 255

        intensity = int(self.top_bright * self.saturation)

        for i in range(16):
            self.neo[i] = (intensity,intensity,intensity);
        self.neo.show()

    def setError(self):
        for i in range(40):
            self.neo[i] = (255,0,0);
        self.neo.show()

    def setReboot(self):
        for i in range(40):
            self.neo[i] = (0,0,255);
        self.neo.show()

    def setOff(self):
        for i in range(40):
            self.neo[i] = (0,0,0);
        self.neo.show()

    def mapRange(self, x, in_min, in_max, out_min, out_max):
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
        status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
        while status == Gst.StateChangeReturn.ASYNC:
            status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
            sleep(0.01)
        if status.state == Gst.State.PLAYING:
            print("SUCCESS!")
            return 1
        else:
            print("FAILURE!")
            return -1

    def changeVolume(self, change):
        self.volume = self.volume + change
        self.audioamplify.set_property('amplification', self.volume)

    def mute(self):
        self.audioamplify.set_property('amplification', 0)

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
    lamp.console = "Fading in..."
    while streamer.volume < lamp.peak and lamp.top_bright < 255:
        if streamer.volume < lamp.peak:
            streamer.changeVolume(0.01)
        if lamp.top_bright < 255:
            lamp.setBulb(1)
        sleep(lamp.fade_rate)

def fadeOut():
    lamp.console = "Fading out..."
    while streamer.volume > 0 and lamp.top_bright > 0:
        if streamer.volume > 0:
            streamer.changeVolume(-0.01)
        if lamp.top_bright > 0:
            lamp.setBulb(-1)
        sleep(lamp.fade_rate)

def changeListener():
    lamp.console = "Connecting..."
    lamp.changing = 0
    tries = 0
    while lamp.changing <= 0:
        lamp.changing = streamer.change(lamp.stream)
        tries = tries + lamp.changing
        print("TRIES: " + str(tries))
        if tries == -3:
            lamp.setError()
            lamp.console = "Error..."
            lamp.state = "error"
            lamp.change = False
            lamp.changing = 1

    if lamp.state != "error":
        lamp.setBase(0)
        fadeIn()
        lamp.change = False
        lamp.console = "Streaming..."


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

    while lamp.state != "start":
        pass

    while True:
        while lamp.change:
            print("SWITCH | " + lamp.state + ": " + str(lamp.stream))
            fadeOut()
            if lamp.state == "streaming":
                changeListener()
            else:
                lamp.setBulb(0)
                streamer.mute()
                lamp.change = False
                lamp.console = "Broadcasting..."
