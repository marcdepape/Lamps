#!/usr/bin/env python
import sys
import gi
#gi.require_version('Gst', '1.0')
#gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

class RTSP_Server:
    def __init__(self):
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer.new()
        self.address = 'localhost'
        self.port = '8554'

        self.server.set_address(self.address)
        self.server.set_service(self.port)

        self.launch_description = "( filesrc location=05Arrows.ogg ! oggdemux ! queue ! rtpvorbispay name=pay0 pt=96 )"

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
