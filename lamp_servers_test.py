#!/usr/bin/env python3
import os
from time import sleep
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer
Gst.init(None)

sleep_time = 5

class Streamer(object):
    def __init__(self):
        self.AMP_ELEMENT_NAME = 'lamp-audio-amplify'
        self.RTSP_ELEMENT_NAME = 'lamp-rtsp-source'
        self.pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        self.volume = 0

        #print("pipeline:", self.pipeline_string)

    def change(self, lamp_num):
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline_string = self.pipeline_template()
        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        url = "rtsp://lamp{}.local:8100/mic".format(lamp_num)
        #print(url)
        self.rtspsrc.set_property('location', url)
        self.audioamplify.set_property('amplification', 0)
        self.pipeline.set_state(Gst.State.PLAYING)
        status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
        while status == Gst.StateChangeReturn.ASYNC:
            status = self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
            sleep(0.01)
        if status.state == Gst.State.PLAYING:
            success = "{} | SUCCESS! | {}".format(lamp_num, sleep_time)
            print(success)
            return 1
        else:
            failure = "{} | FAILURE! | {}".format(lamp_num, sleep_time)
            print(failure)
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


if __name__ == '__main__':
    print("")
    print("--------------------------------------------")
    print("LAMP SERVER TEST")
    print("")
    print()

    streamer = Streamer()
    next_lamp = 0

    while True:
        connection = 0
        while connection == 0:
            connection = streamer.change(next_lamp)

        if connection == 1:
            os.system("gst-launch-1.0 rtspsrc latency=500 location=rtsp://lamp{}.local:8100/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,rate=44100,channels=1 ! alsasink &".format(next_lamp))
            sleep(sleep_time)
            os.system("killall -9 gst-launch-1.0")
        elif connection == -1:
            sleep(5)

        next_lamp = next_lamp + 1
        if next_lamp > 5:
            next_lamp = 0
            if sleep_time < 300:
                sleep_time = sleep_time * 2
