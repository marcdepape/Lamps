import zmq
import json
import alsaaudio as alsa
from threading import Thread
from time import sleep
import subprocess
import board
import neopixel
import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

Gst.init(None)

# extended Gst.Bin that overrides do_handle_message and adds debugging
class ExtendedBin(Gst.Bin):
    #context = zmq.Context()
    #zmq_socket = context.socket(zmq.PUB)
    #zmq_socket.bind("tcp://127.0.0.1:8103")

    def do_handle_message(self,message):
        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print("ERROR:", message.src.get_name(), ":", error.message)
            if debug:
                print ("Debug info: " + debug)
        elif message.type == Gst.MessageType.EOS:
            print ("End of stream")
        elif message.type == Gst.MessageType.STATE_CHANGED:
            #pass
            oldState, newState, pendingState = message.parse_state_changed()
            print ("State changed -> old:{}, new:{}, pending:{}".format(oldState,newState,pendingState))
        elif message.type == Gst.MessageType.ELEMENT:
            structure = message.get_structure()
            name = structure.get_name()

            if name == "level":
                value = structure.get_value("rms")
                #zmq_socket.send_string(str(value[0]))
                level = value[0]
                print(level)
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

        # SERVER
        server_context = zmq.Context()
        self.publish = server_context.socket(zmq.PUB)
        self.publish.connect("tcp://armadillo.local:8101")
        self.publish.set_hwm(1)

        # CLIENT
        client_context = zmq.Context()
        self.subscribe = client_context.socket(zmq.SUB)
        self.subscribe.connect("tcp://armadillo.local:8102")
        self.subscribe.setsockopt(zmq.SUBSCRIBE, b'')
        self.subscribe.set_hwm(1)

        # CLIENT
        local_context = zmq.Context()
        self.levels = local_context.socket(zmq.SUB)
        self.levels.connect("tcp://localhost:8103")
        self.levels.setsockopt(zmq.SUBSCRIBE, b'')
        self.levels.set_hwm(1)

    def compare(self):
        if self.in_update["command"] != self.command:
            self.command = self.in_update["command"]
            if self.command == "reboot":
                self.command = "complete"
                self.setReboot()
                print("REBOOT!")
                #os.system("reboot now")
            if self.command == "start":
                self.state = "start"
                self.command = "complete"

        if self.in_update["rate"] != self.fade_rate:
            self.fade_rate = self.in_update["fade"]

        if self.in_update["peak"] != self.peak:
            self.peak = self.in_update["peak"]

        if self.in_update["saturation"] != self.saturation:
            self.saturation = self.in_update["saturation"]
            if self.state == "streaming":
                self.setBulb(100)

        if self.in_update["stream"] != self.stream:
            self.stream = self.in_update["stream"]
            self.change = True
            if self.stream == -1:
                self.state = "broadcasting"
            else:
                self.state = "streaming"

    def statusOut(self):
        while self.report:
            self.out_status = json.dumps({"id": self.id,
                                        "fade": self.fade_rate,
                                        "saturation": self.saturation,
                                        "stream": self.stream,
                                        "state": self.state,
                                        "command": self.command,
                                        "mic": self.mic_signal,
                                        "console": self.console})
            self.publish.send_json(self.out_status)
            sleep(1)

    def updateIn(self):
        while self.report:
            update = self.subscribe.recv_json()
            update = json.loads(update)
            if update["lamp"] == self.id:
                self.in_update = update
                self.compare()
                #print("IN UPDATE: " + str(self.in_update) + " | " + str(self.change))

    def micLevels(self):
        while self.report:
            self.mic_signal = self.levels.recv_string()
            if self.state == "broadcasting":
                print(self.mic_signal)
                self.pulse(self.mic_signal)

    def pulse(self, rms):
        self.bottom_bright = 100 + float(rms)
        self.bottom_bright = self.constrain(self.bottom_bright, 55, 90)
        self.bottom_bright = self.mapRange(self.bottom_bright, 55, 90, 0, 255)
        self.bottom_bright = int(self.bottom_bright * self.saturation)
        self.setBase(self.bottom_bright)

    def setBase(self, value):
        self.bottom_bright = value

        if self.bottom_bright < 0:
            self.bottom_bright = 0
        if self.bottom_bright > 255:
            self.bottom_bright = 255

        intensity = int(self.bottom_bright * self.saturation)

        for i in range(16, self.num_pixels):
            self.neo[i] = (intensity,intensity,intensity);
        self.neo.show()

    def setBulb(self, value):
        value = self.mapRange(value, 0, 100, 0, 255)
        self.top_bright = self.top_bright + value

        if self.top_bright < 0:
            self.top_bright = 0
        if self.top_bright > 255:
            self.top_bright = 255

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


if __name__ == "__main__":
    print("")
    print("--------------------------------------------")
    print("LAUNCH LAMP")
    print("")

    lamp = Lamp(lamp_id)
    stream = RTSP_Server(this_lamp)
    sleep(3)

    publisher = Thread(target=lamp.statusOut, args=())
    publisher.start()
    subscriber = Thread(target=lamp.updateIn, args=())
    subscriber.start()
    mic = Thread(target=lamp.micLevels, args=())
    mic.start()

    lamp.setBulb(0)
    lamp.setBase(0)

    while True:
        pass
