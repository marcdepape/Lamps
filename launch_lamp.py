#!/usr/bin/env python
import zmq
import json
import alsaaudio
from threading import Thread
from time import sleep
import subprocess
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
    def __init__(self):
        self.live = False
        self.volume = 0
        self.peak = 1.5
        self.fade_rate = 0.05
        self.id = 0
        self.stream = 0
        self.server = True
        self.fade = "in"
        self.state = "listening"
        self.in_update = ""
        self_out_status = ""
        self.report = True

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

    def status(self):
        while self.report:
            self.out_status = json.dumps({"id": self.lamp_id, "live": self.live, "fade": self.fade, "server": self.server, "stream": self.stream, "state": self.state})
            self.publish.send_json(self.out_update)
            sleep(1)

    def update(self):
        update = self.subscribe.recv_json()
        update = json.loads(update)
        if update["lamp"] == self.lamp_id:
            self.in_update = update
            return self.in_update
        else:
            return -1

class Streamer(object):
    def __init__(self):
        self.AMP_ELEMENT_NAME = 'lamp-audio-amplify'
        self.RTSP_ELEMENT_NAME = 'lamp-rtsp-source'
        pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        self.volume = 0

        print("pipeline:", pipeline_string)

    def start(self, lamp_num):
        url = "rtsp://lamp{}.local:8100/mic".format(lamp_num)
        print(url)
        self.rtspsrc.set_property('location', url)
        self.audioamplify.set_property('amplification', 0)
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.READY)

    def getVolume(self):
        return self.audioamplify.get_property('amplification')

    def setVolume(self, level):
        self.audioamplify.set_property('amplification', level)

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
lamp = Lamp()

def fadeIn():
    while streamer.volume < lamp.peak:
        streamer.changeVolume(0.01)
        sleep(lamp.fade_rate)
    lamp.fade = "in"

def fadeOut():
    while streamer.volume > 0:
        streamer.changeVolume(-0.01)
        sleep(lamp.fade_rate)
    lamp.fade = "out"

if __name__ == "__main__":
    print("")
    print("--------------------------------------------")
    print("MAIN")
    print("")

    publisher = Thread(target=lamp.status, args=())
    publisher.start()
    subscriber = Thread(target=lamp.update, args=())
    subscriber.start()

    while True:
        if not lamp.live:
            streamer.start(2)
            lamp.is_live = True

        fadeIn()
        sleep(15)
        fadeOut()
        sleep(5)
        print("SWITCH!")
