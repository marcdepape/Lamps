#!/usr/bin/env python
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

class RTSP_Server:
    def __init__(self):
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer.new()
        self.address = 'lamp4.local'
        self.port = '8554'

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        #self.launch_description = "( alsasrc ! queue leaky=downstream max-size-buffers=16 ! queue ! audioconvert ! queue ! vorbisenc quality=0.7 ! queue leaky=downstream max-size-buffers=16 ! rtpvorbispay name=pay0 pt=96)"
        self.launch_description = "( alsasrc buffer-time=2000 ! audio/x-raw,rate=44100,channels=2 ! audioconvert ! queue ! vorbisenc quality=0.7 ! queue ! rtpvorbispay name=pay0 pt=96)"

        '''
        marc@armadillo:~$ gst-launch-1.0 rtspsrc location=rtsp://localhost:8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
        '''

        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_launch(self.launch_description)
        self.factory.set_shared(True)
        print(self.factory.get_launch())
        self.mount_points = self.server.get_mount_points()
        self.mount_points.add_factory('/mic', self.factory)

        self.server.attach(None)
        print('Stream ready: ' + str(self.server.get_address()))
        GLib.MainLoop().run()


server = RTSP_Server()
