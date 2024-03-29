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

#mic1 = alsaaudio.Mixer('Mic 1')
mic2 = alsaaudio.Mixer('Mic 2')
#ADC = alsaaudio.Mixer('ADC')
#ADC.setvolume(80)
#mic1.setvolume(0)
mic2.setvolume(60)

'''
gst-launch-1.0 rtspsrc latency=1024 location=rtsp://lamp1.local:8100/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! alsasink
'''

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
        print(self.factory.get_launch())
        print ("RTSP server is ready")

        mainloop = GLib.MainLoop()
        m = Thread(name="mainloop", target=mainloop.run)
        m.daemon = True
        m.start()

class Streamer(object):
    def __init__(self):
        self.AMP_ELEMENT_NAME = 'lamp-audio-amplify'
        self.RTSP_ELEMENT_NAME = 'lamp-rtsp-source'
        self.pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        self.volume = 0

        print("pipeline:", self.pipeline_string)

    def change(self, lamp_num):
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline_string = self.pipeline_template()
        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        url = "rtsp://lamp{}.local:8100/mic".format(lamp_num)
        print(url)
        self.rtspsrc.set_property('location', url)
        self.audioamplify.set_property('amplification', 0)
        self.pipeline.set_state(Gst.State.PLAYING)
        status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
        while status == Gst.StateChangeReturn.ASYNC:
            status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
            sleep(0.01)
        if status.state == Gst.State.PLAYING:
            print("SUCCESS!")
            return 1
        else:
            print("FAILURE!")
            return -1

    def changeVolume(self, change):
        self.volume = self.volume + change
        self.audioamplify.set_property('amplification', self.volume)

    def mute(self):
        self.audioamplify.set_property('amplification', 0)

    def pipeline_template(self):
        return ("rtspsrc latency=500 name={} ! "
                "queue ! "
                "rtpvorbisdepay ! "
                "vorbisdec ! "
                "audioamplify name={} ! "
                "audioconvert ! "
                "audio/x-raw,format=S16LE,rate=44100,channels=1 ! "
                "alsasink"
                ).format(self.RTSP_ELEMENT_NAME, self.AMP_ELEMENT_NAME)

class Lamp(object):
    def __init__(self, lamp_num):
        self.id = lamp_num
        self.live = False
        self.volume = 0
        self.peak = 1.5
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.stream = 255
        self.change = False
        self.pulse_point = 65
        self.record = 60
        self.state = "?"
        self.in_update = ""
        self.out_status = ""
        self.console = "Launching..."
        self.report = True
        self.mic_signal = 0.0
        self.top_bright = 0
        self.bottom_bright = 0
        self.command = "null"

        # NeoPixel
        self.pixel_pin = board.D12
        self.num_pixels = 40
        self.neo = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB
        )
        self.setOff()

        # ENCODER
        self.btn = 16
        self.dt = 23
        self.clk = 24
        self.top_rotation = 0
        self.bottom_rotation = 0
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.last_clk = GPIO.input(self.clk)
        self.last_btn = GPIO.input(self.btn)

        # SERVER
        server_context = zmq.Context()
        self.publish = server_context.socket(zmq.PUB)
        self.publish.connect("tcp://downy.local:8101")
        self.publish.set_hwm(1)

        # CLIENT
        client_context = zmq.Context()
        self.subscribe = client_context.socket(zmq.SUB)
        self.subscribe.connect("tcp://downy.local:8102")
        self.subscribe.setsockopt(zmq.SUBSCRIBE, b'')
        self.subscribe.set_hwm(1)

        # CLIENT
        levels_context = zmq.Context()
        self.levels = levels_context.socket(zmq.SUB)
        self.levels.connect("tcp://localhost:8103")
        self.levels.setsockopt(zmq.SUBSCRIBE, b'')
        self.levels.set_hwm(1)

    def compare(self):
        if self.in_update["command"] != self.command:
            self.command = self.in_update["command"]
            if self.command == "start":
                pass
                #self.state = "start"
                #self.command = "complete"
            if self.command == "complete":
                self.console = "Complete..."
                self.command = "null"
            if self.command == "reset":
                self.console = "Reseting..."

        if self.in_update["rate"] != self.fade_rate:
            self.fade_rate = self.in_update["fade"]

        if self.in_update["peak"] != self.peak:
            self.peak = self.in_update["peak"]

        if self.in_update["saturation"] != self.saturation:
            self.saturation = self.in_update["saturation"]
            if self.state == "streaming":
                self.changeBulb(0)
                self.changeBase(0)

        if self.in_update["record"] != self.record:
            self.record = self.in_update["record"]
            mic2.setvolume(self.record)
            self.console = "Rec: {}".format(self.record)

        if self.in_update["pulse"] != self.pulse_point:
            self.pulse_point = self.in_update["pulse"]

        if self.in_update["stream"] != self.stream:
            self.stream = self.in_update["stream"]
            self.change = True
            if self.stream == -1:
                self.state = "broadcasting"
            else:
                self.state = "streaming"
            self.console = "Switching to {}".format(self.stream)

    def statusOut(self):
        while self.report:
            self.out_status = json.dumps({"id": self.id,
                                        "fade": self.fade_rate,
                                        "saturation": self.saturation,
                                        "stream": self.stream,
                                        "state": self.state,
                                        "command": self.command,
                                        "pulse": self.pulse_point,
                                        "mic": self.mic_signal,
                                        "record": self.record,
                                        "console": self.console})
            self.publish.send_json(self.out_status)
            sleep(0.5)

    def updateIn(self):
        while self.report:
            update = self.subscribe.recv_json()
            update = json.loads(update)
            if update["lamp"] == self.id:
                self.in_update = update
                self.compare()

    def encoder(self):
        clk_state = GPIO.input(self.clk)
        dt_state = GPIO.input(self.dt)
        #btn_state = GPIO.input(self.btn)

        increment = 4
        self.counter += 1

        if clk_state != self.last_clk:
            counter = 0
            if dt_state != clk_state:
                if self.state == "streaming":
                    if self.bottom_rotation > 0:
                        self.bottom_rotation -= increment*2
                        if self.bottom_rotation < 0:
                            self.bottom_rotation = 0
                    elif self.top_rotation < 255:
                        self.top_rotation += increment*2
                        if self.top_rotation > 255:
                            self.top_rotation = 255
                elif self.state == "broadcasting":
                    if self.top_rotation < 255:
                        self.top_rotation += increment
                        if self.top_rotation > 255:
                            self.top_rotation = 255
            else:
                if self.state == "streaming":
                    if self.top_rotation > 0:
                        self.top_rotation -= increment*2
                        if self.top_rotation < 0:
                            self.top_rotation = 0
                    elif self.bottom_rotation < 255:
                        self.bottom_rotation += increment*2
                        if self.bottom_rotation > 255:
                            self.bottom_rotation = 255
                elif self.state == "broadcasting":
                    if self.top_rotation > 0:
                        self.top_rotation -= increment
                        if self.top_rotation < 0:
                            self.top_rotation = 0

            if self.state == "streaming":
                self.writeBulb(self.top_rotation)
                self.writeBase(self.bottom_rotation)
            elif self.state == "broadcasting":
                self.writeBulb(self.top_rotation)

            if self.top_rotation > 200 and self.state == "broadcasting" and self.command != "listen" and self.command != "complete":
                print("MANUAL LISTEN!")
                self.command = "listen"
            elif self.bottom_rotation > 200 and self.state == "streaming" and self.command != "broadcast" and self.command != "complete":
                print("MANUAL BROADCAST!")
                self.command = "broadcast"

        self.last_clk = clk_state
        #self.last_btn = btn_state

        if self.counter > 20:
            if self.top_rotation > 0 and self.state == "broadcasting" and self.command != "listen":
                self.top_rotation -= 1
                self.writeBulb(self.top_rotation)
            if self.state == "streaming" and self.command != "broadcast":
                if self.bottom_rotation > 0:
                    self.bottom_rotation -= 1
                    self.writeBase(self.bottom_rotation)
                elif self.top_rotation < 255:
                    self.top_rotation += 1
                    self.writeBulb(self.top_rotation)
            self.counter = 0

    def micLevels(self):
        while self.report:
            self.mic_signal = self.levels.recv_string()

            if self.mic_signal != "error":
                if self.state == "broadcasting":
                    self.pulse(self.mic_signal)
            else:
                self.command = "error"

    def pulse(self, rms):
        self.bottom_bright = 100 + float(rms)
        self.bottom_bright = self.constrain(self.bottom_bright, self.pulse_point, 95)
        self.bottom_bright = self.mapRange(self.bottom_bright, self.pulse_point, 95, 0, 255)
        self.console = "{} | {}".format(self.record, self.bottom_bright)

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

    def setError(self):
        for i in range(40):
            self.neo[i] = (255,0,0);
        self.neo.show()

    def setReboot(self):
        for i in range(40):
            self.neo[i] = (0,0,255);
        self.neo.show()

    def setOff(self):
        for i in range(40):
            self.neo[i] = (0,0,0);
        self.neo.show()

    def mapRange(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

def fadeIn():
    lamp.console = "Fading in..."
    lamp.writeBase(0)
    while streamer.volume < lamp.peak or lamp.top_bright < 255:
        if streamer.volume < lamp.peak:
            streamer.changeVolume(0.01)
        if lamp.top_bright < 255:
            lamp.changeBulb(1)
        sleep(lamp.fade_rate)

#------------------------------------------------------------------------------

def fadeOut():
    lamp.writeBase(0)
    lamp.console = "Fading out..."
    while streamer.volume > 0 or lamp.top_bright > 0:
        if streamer.volume > 0:
            streamer.changeVolume(-0.01)
        if lamp.top_bright > 0:
            lamp.changeBulb(-1)
        sleep(lamp.fade_rate)
        lamp.console = "{:.2f} | {}".format(streamer.volume, lamp.top_bright)
    lamp.writeBulb(0)
    streamer.mute()

    lamp.console = "Faded..."

def changeListener():
    if lamp.stream == -1:
        lamp.state = "broadcasting"
        return

    lamp.console = "Connecting..."
    changing = -1
    tries = 0
    current_stream = lamp.stream
    current_state = lamp.state

    while changing == -1:
        if current_stream != lamp.stream or current_state != lamp.state:
            return

        changing = streamer.change(lamp.stream)
        tries = tries + changing
        print("TRIES: " + str(tries))
        if tries == -5:
            lamp.setError()
            lamp.console = "Error..."
            lamp.command = "error"
        sleep(1)

    if lamp.command == "reset":
        lamp.command = "null"
        lamp.writeBulb(0)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    print("")
    print("--------------------------------------------")
    print("LAUNCH LAMP")
    print("")
    print()

    share = RTSP_Server(lamp_id)
    streamer = Streamer()
    lamp = Lamp(lamp_id)

    publisher = Thread(target=lamp.statusOut, args=())
    publisher.start()
    subscriber = Thread(target=lamp.updateIn, args=())
    subscriber.start()
    mic = Thread(target=lamp.micLevels, args=())
    mic.start()

    lamp.writeBulb(0)
    lamp.writeBase(0)

    while lamp.state == "?":
        pass

    sleep(3)

    lamp.change = True

    while True:
        while lamp.change:
            lamp.console = "Switching..."

            if lamp.state != "streaming" and lamp.state != "broadcasting":
                if lamp.stream == -1:
                    lamp.state = "broadcasting"
                else:
                    lamp.state = "streaming"

            lamp.top_rotation = 0
            lamp.bottom_rotation = 0
            fadeOut()

            if lamp.state == "streaming":
                changeListener()
                fadeIn()
                lamp.console = "Streaming..."
                lamp.change = False
            elif lamp.state == "broadcasting":
                streamer.mute()
                lamp.console = "Broadcasting..."
                lamp.change = False

        lamp.encoder()
        sleep(0.001)
