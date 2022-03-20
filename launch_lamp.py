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

streams = [
    "://lamp0.local:8100",
    "tcp://lamp1.local:8100",
    "tcp://lamp2.local:8100",
    "tcp://lamp3.local:8100",
    "tcp://lamp4.local:8100",
    "tcp://lamp5.local:8100",
]

'''
gst-launch-1.0 rtspsrc latency=250 location=rtsp://lamp2.local:8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
'''

class Lamp(object):
    def __init__(self):
        self.is_live = True
        self.is_broadcasting = False
        self.is_listening = False
        self.volume = 0
        self.id = 0
        self.stream = 0
        self.audio = None
        self.listen = None
        self.broadcast = None

class RTSP_Server:
    def __init__(self, lamp_number):
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer.new()
        self.address = 'lamp{}.local'.format(lamp_number)
        self.port = '8100'

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        self.launch_description = "( alsasrc ! queue leaky=downstream max-size-buffers=16 ! audio/x-raw,format=S16LE,rate=44100,channels=2 ! audioconvert ! vorbisenc quality=0.7 ! queue leaky=downstream max-size-buffers=16 ! rtpvorbispay name=pay0 pt=96 )"

        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_launch(self.launch_description)
        self.factory.set_shared(True)
        print(self.factory.get_launch())
        self.mount_points = self.server.get_mount_points()
        self.mount_points.add_factory('/mic', self.factory)

        self.server.attach(None)
        print('Stream ready at: ' + str(self.server.get_address()))
        GLib.MainLoop().run()

class Streamer(object):
    def __init__(self):
        pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(AMP_ELEMENT_NAME)
        self.volume = 1

        print("pipeline:", pipeline_string)

    def start(self, lamp_num: str):
        url = "rtsp://lamp{}.local:8100/mic".format(lamp_num)

        self.rtspsrc.set_property('location', url)
        self.pipeline.set_state(Gst.State.PLAYING)
        print(url)

    def stop(self):
        self.pipeline.set_state(Gst.State.READY)

    def volume(self):
        return self.audioamplify.get_property('amplification')

    def volume(self, volume):
        self.audioamplify.set_property('amplification', volume)

    def pipeline_template():
        return ("rtspsrc debug=TRUE latency=250 name={} ! "
                "queue ! "
                "rtpvorbisdepay ! "
                "vorbisdec ! "
                "audioamplify name={} ! "
                "audioconvert ! "
                "audio/x-raw,format=S16LE,channels=2 ! "
                "alsasink"
                ).format(RTSP_ELEMENT_NAME, AMP_ELEMENT_NAME)

streamer = Streamer()
server = RTSP_Server(lamp_id)
