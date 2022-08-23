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

rms_level = 0

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
            #local.send_string("error")
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
                level = structure.get_value("rms")
                rms_level = level[0]
                #print(str(name) + ": " + str(value[0]))
                #local.send_string(str(value[0]))

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

class Lamp(object):
    def __init__(self):
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.pulse_point = 65
        self.mic_signal = 0.0
        self.top_bright = 0
        self.bottom_bright = 0

        # NeoPixel
        self.pixel_pin = board.D12
        self.num_pixels = 40
        self.neo = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB
        )
        self.setOff()

        # CLIENT
        levels_context = zmq.Context()
        self.levels = levels_context.socket(zmq.SUB)
        self.levels.connect("tcp://localhost:8103")
        self.levels.setsockopt(zmq.SUBSCRIBE, b'')
        self.levels.set_hwm(1)

    def micLevels(self):
            print("micLevels")
            self.mic_signal = self.levels.recv_string()

            if self.mic_signal == "loop":
                print("THIS IS A LOOP")
            else:
                print(self.mic_signal)
                self.pulse(self.mic_signal)

            #if self.mic_signal != "error":

            #else:
            #    for i in range(16, self.num_pixels):
            #        self.neo[i] = (255,0,0);

    def pulse(self, rms):
        self.bottom_bright = 100 + float(rms)
        self.bottom_bright = self.constrain(self.bottom_bright, self.pulse_point, 95)
        self.bottom_bright = self.mapRange(self.bottom_bright, self.pulse_point, 95, 0, 255)

        if self.bottom_bright < 0:
            self.bottom_bright = 0
        if self.bottom_bright > 255:
            self.bottom_bright = 255

        self.writeBase(self.bottom_bright)

    def changeBase(self, value):
        value = self.mapRange(value, 0, 100, 0, 255)
        self.bottom_bright = self.bottom_bright + value

        if self.bottom_bright < 0:
            self.bottom_bright = 0
        if self.bottom_bright > 255:
            self.bottom_bright = 255

        self.writeBase(self.bottom_bright)

    def writeBase(self, value):
        self.top_bright = value
        intensity = int(self.top_bright * self.saturation)
        for i in range(16, self.num_pixels):
            self.neo[i] = (intensity,intensity,intensity);
        self.neo.show()

    def changeBulb(self, value):
        value = self.mapRange(value, 0, 100, 0, 255)
        self.top_bright = self.top_bright + value

        if self.top_bright < 0:
            self.top_bright = 0
        if self.top_bright > 255:
            self.top_bright = 255

        self.writeBulb(self.top_bright)

    def writeBulb(self, value):
        self.top_bright = value
        intensity = int(self.top_bright * self.saturation)
        for i in range(16):
            self.neo[i] = (intensity,intensity,intensity);
        self.neo.show()

    def setOff(self):
        for i in range(40):
            self.neo[i] = (0,0,0);
        self.neo.show()

    def mapRange(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))



if __name__ == '__main__':
    lamp = Lamp()

    lamp.writeBase(0)

    lamp.top_bright = 255

    while lamp.top_bright > 0:
        lamp.changeBulb(-1)
        sleep(lamp.fade_rate)

    lamp_server = RTSP_Server(lamp_id)

    while True:
        lamp.pulse(rms_level)
        sleep(0.01)
