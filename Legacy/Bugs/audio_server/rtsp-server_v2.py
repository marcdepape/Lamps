#!/usr/bin/env python
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GstRtspServer

class RTSP_Server:
    def __init__(self):
        self.server = GstRtspServer.RTSPServer.new()
        self.address = 'localhost'
        self.port = '8554'
        self.launch_description = '( playbin uri=/Users/marcdepape/Desktop/gtspserver-test-tlw.mp3 )'

        self.server.set_address(self.address)
        self.server.set_service(self.port)
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch(self.launch_description)
        self.factory.set_shared(True)
        self.mount_points = self.server.get_mount_points()
        self.mount_points.add_factory('/mic', self.factory)

        self.server.attach(None)
        print('Stream ready')
        GObject.MainLoop().run()


server = RTSP_Server()
