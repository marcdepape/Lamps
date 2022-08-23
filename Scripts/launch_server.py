#!/usr/bin/env python
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

mic2 = alsaaudio.Mixer('Mic 2')
mic2.setvolume(60)

pixel_pin = board.D12
num_pixels = 40
ORDER = neopixel.GRB
pulse_min = 65
pulse_max = 95

neo = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

def pulse(self, rms):
    bottom_bright = 100 + float(rms)
    bottom_bright = constrain(bottom_bright, pulse_min, pulse_max)
    bottom_bright = mapRange(bottom_bright, pulse_min, pulse_max, 0, 255)

    if bottom_bright < 0:
        bottom_bright = 0
    if bottom_bright > 255:
        bottom_bright = 255

    writeBase(bottom_bright)

def mapRange(self, x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def constrain(self, val, min_val, max_val):
    return min(max_val, max(min_val, val))

def writeBulb(self, value):
    top_bright = value
    intensity = int(top_bright * saturation)
    for i in range(16):
        neo[i] = (intensity,intensity,intensity);
    neo.show()

def writeBase(self, value):
    intensity = int(value * saturation)
    for i in range(16, num_pixels):
        neo[i] = (intensity,intensity,intensity);
    neo.show()

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
                pulse(level[0])

        else :
            pass
            #print("Some other message type: " + str(message.type))

        #call base handler to enable message propagation
        Gst.Bin.do_handle_message(self,message)

class RtspMediaFactory(GstRtspServer.RTSPMediaFactory, ):

    def __init__(self, this_lamp):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        lamp_bulb = this_lamp

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
    def __init__(self, this_lamp, lamp_number):
        self.rtspServer = GstRtspServer.RTSPServer()

        self.address = 'lamp{}.local'.format(lamp_number)
        self.port = '8100'

        self.rtspServer.set_address(self.address)
        self.rtspServer.set_service(self.port)

        self.factory = RtspMediaFactory(this_lamp)
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
    lamp_server = RTSP_Server(lamp, lamp_id)

    while True:
        sleep(0.01)
