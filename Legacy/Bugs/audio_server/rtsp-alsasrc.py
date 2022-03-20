#!/usr/bin/env python
import sys
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

        self.server = GstRtspServer.RTSPServer.new()
        self.address = 'lamp{}.local'.format(lamp_number)
        self.port = '8100'

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        #self.launch_description = "( alsasrc ! queue leaky=downstream max-size-buffers=16 ! queue ! audioconvert ! queue ! vorbisenc quality=0.7 ! queue leaky=downstream max-size-buffers=16 ! rtpvorbispay name=pay0 pt=96)"
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


server = RTSP_Server(lamp_id)
