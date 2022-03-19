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
        self.address = 'localhost'
        self.port = '8554'

        self.server.set_address(self.address)
        self.server.set_service(self.port)

        #self.launch_description = '( playbin uri=file:///home/marc/Projects/Lamps/Legacy/Bugs/audio_server/05Arrows.mp3 )'

        self.launch_description = "( filesrc location=05Arrows.ogg ! oggdemux ! queue ! rtpvorbispay name=pay0 pt=96 )"

        '''
        marc@armadillo:~$ gst-launch-1.0 rtspsrc location=rtsp://localhost:8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
        '''

        #self.launch_description = "( filesrc location=05Arrows.ogg ! oggdemux name=d ! queue ! rtptheorapay name=pay0 pt=96 ! queue ! rtpvorbispay name=pay1 pt=97 )".format(**locals())
        #self.launch_description = '( filesrc location=05Arrows.mp3 ! mpegaudioparse ! mpg123audiodec ! audioconvert ! audioresample ! autoaudiosink )'
        #https://stackoverflow.com/questions/60230807/convert-gstreamer-pipeline-to-python-code

        #self.pipeline = Gst.Pipeline.new()

        #self.source = Gst.ElementFactory.make("playbin", None)
        #self.source.set_property("uri", "file:///home/marc/Projects/Lamps/Legacy/Bugs/audio_server/05Arrows.mp3")

        #self.pipeline.add(self.source)


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

#https://stackoverflow.com/questions/47396372/write-opencv-frames-into-gstreamer-rtsp-server-pipeline
#https://github.com/mad4ms/python-opencv-gstreamer-examples/blob/master/gst_rtsp_server.py
#https://github.com/tamaggo/gstreamer-examples/blob/master/test_gst_rtsp_server.py

'''
 str = g_strdup_printf ("( "
      "filesrc location=%s ! oggdemux name=d "
      "d. ! queue ! rtptheorapay name=pay0 pt=96 "
      "d. ! queue ! rtpvorbispay name=pay1 pt=97 " ")", argv[1]);
'''
