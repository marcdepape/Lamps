#!/usr/bin/env python
import zmq
import json
import alsaaudio
from threading import Thread
from time import sleep
import subprocess
import board
from RPi import GPIO
import neopixel
import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

Gst.init(None)

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

local_context = zmq.Context()
local = local_context.socket(zmq.PUB)
local.bind("tcp://127.0.0.1:8103")
local.set_hwm(1)

mic2 = alsaaudio.Mixer('Mic 2')
mic2.setvolume(60)

# extended Gst.Bin that overrides do_handle_message and adds debugging
class ExtendedBin(Gst.Bin):
    def do_handle_message(self,message):
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print("ERROR:", message.src.get_name(), ":", error.message)
            if debug:
                print ("Debug info: " + debug)
            local.send_string("error")
        elif message.type == Gst.MessageType.EOS:
            print ("End of stream")
        elif message.type == Gst.MessageType.STATE_CHANGED:
            pass
            #oldState, newState, pendingState = message.parse_state_changed()
            #print ("State changed -> old:{}, new:{}, pending:{}".format(oldState,newState,pendingState))
        elif message.type == Gst.MessageType.ELEMENT:
            structure = message.get_structure()
            name = structure.get_name()

            if name == "level":
                value = structure.get_value("rms")
                print(value[0])
                local.send_string(str(value[0]))

                #level = value[0]
        else :
            pass
            #print("Some other message type: " + str(message.type))

        #call base handler to enable message propagation
        Gst.Bin.do_handle_message(self,message)

class RtspMediaFactory(GstRtspServer.RTSPMediaFactory, ):

    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        pipelineCmd = ("alsasrc ! "
                        "queue max-size-buffers=1024 ! "
                        "audio/x-raw,format=S16LE,rate=44100,channels=1 ! "
                        "audioconvert ! "
                        "audiowsinclimit cutoff=40000 ! "
                        "level name=wavelevel interval=50000000 "
                        "post-messages=TRUE ! "
                        "audioconvert ! "
                        "queue ! "
                        "vorbisenc quality=0.3 ! "
                        "queue ! "
                        "rtpvorbispay name=pay0 pt=96"
                        ).format()

        self.pipeline = Gst.parse_launch(pipelineCmd)
        print ("Pipeline created: " + pipelineCmd)

        # creates extended Gst.Bin with message debugging enabled
        extendedBin = ExtendedBin("extendedBin")

        # Gst.pipeline inherits Gst.Bin and Gst.Element so following is possible
        extendedBin.add(self.pipeline)

        # creates new Pipeline and adds extended Bin to it
        self.extendedPipeline = Gst.Pipeline.new("extendedPipeline")
        self.extendedPipeline.add(extendedBin)

        return self.extendedPipeline

class RTSP_Server(GstRtspServer.RTSPServer):
    def __init__(self, lamp_number):
        self.rtspServer = GstRtspServer.RTSPServer()

        self.address = 'lamp{}.local'.format(lamp_number)
        self.port = '8100'

        self.rtspServer.set_address(self.address)
        self.rtspServer.set_service(self.port)

        self.factory = RtspMediaFactory()
        self.factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/mic", self.factory)
        self.rtspServer.attach(None)
        lamp_name = 'LAMP{}'.format(lamp_number)
        print("FACTORY FOR " + lamp_name)
        print(self.factory.get_launch())
        print ("RTSP server is ready")

        mainloop = GLib.MainLoop()
        m = Thread(name="mainloop", target=mainloop.run)
        m.daemon = True
        m.start()

if __name__ == '__main__':
    print("")
    print("--------------------------------------------")
    print("LAUNCH LAMP")
    print("")
    print()

    lamp_server = RTSP_Server(lamp_id)

    sleep(3)

    while True:
        sleep(0.001)
