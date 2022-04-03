#!/usr/bin/env python
import zmq
import sys
import gi
import subprocess
from threading import Thread

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

Gst.init(None)

context = zmq.Context()
local = context.socket(zmq.PUB)
local.bind("tcp://127.0.0.1:8103")
local.set_hwm(1)

# extended Gst.Bin that overrides do_handle_message and adds debugging
class ExtendedBin(Gst.Bin):
    def do_handle_message(self,message):
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print("ERROR:", message.src.get_name(), ":", error.message)
            if debug:
                print ("Debug info: " + debug)
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
                local.send_string(str(value[0]))
                #level = value[0]
        else :
            print("Some other message type: " + str(message.type))

        #call base handler to enable message propagation
        Gst.Bin.do_handle_message(self,message)

class RtspMediaFactory(GstRtspServer.RTSPMediaFactory):

    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        pipelineCmd = "alsasrc ! queue ! audio/x-raw,format=S16LE,rate=44100,channels=1 ! level name=wavelevel interval=100000000 post-messages=TRUE ! audioconvert ! vorbisenc quality=0.4 ! queue ! rtpvorbispay name=pay0 pt=96"

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
        print(self.factory.get_launch())
        print ("RTSP server is ready")

        mainloop = GLib.MainLoop()
        m = Thread(name="mainloop", target=mainloop.run)
        m.daemon = True
        m.start()

if __name__ == '__main__':
    s = RTSP_Server(3)

    while True:
        pass
