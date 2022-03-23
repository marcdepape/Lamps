#!/usr/bin/env python
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

'''
gst-launch-1.0 rtspsrc location=rtsp://lamp2.local:8100/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
'''

class RTSP_Server:
    def __init__(self, lamp_number):
        Gst.init(None)

        self.rtsp = GstRtspServer.RTSPServer.new()
        self.address = 'lamp{}.local'.format(lamp_number)
        self.port = '8100'

        self.rtsp.set_address(self.address)
        self.rtsp.set_service(self.port)
        self.launch_description = "( alsasrc ! queue ! audio/x-raw,format=S16LE,rate=44100,channels=2 ! audioconvert ! vorbisenc quality=0.4 ! queue ! rtpvorbispay name=pay0 pt=96 )"

        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_launch(self.launch_description)
        self.factory.set_shared(True)
        print(self.factory.get_launch())
        self.mount_points = self.rtsp.get_mount_points()
        self.mount_points.add_factory('/mic', self.factory)

        self.rtsp.attach(None)
        print('Stream ready at: ' + str(self.rtsp.get_address()))

        self.local = GstRtspServer.RTSPServer.new()
        self.address = 'localhost'
        self.port = '8105'

        self.local.set_address(self.address)
        self.local.set_service(self.port)
        self.launch_description = "( alsasrc ! audioconvert ! rtpL16pay name=pay1 pt=97 )"

        self.factory_local = GstRtspServer.RTSPMediaFactory.new()
        self.factory_local.set_launch(self.launch_description)
        self.factory_local.set_shared(True)
        print(self.factory_local.get_launch())
        self.mount_points_local = self.local.get_mount_points()
        self.mount_points_local.add_factory('/levels', self.factory_local)

        self.local.attach(None)

        GLib.MainLoop().run()

server = RTSP_Server(lamp_id)
