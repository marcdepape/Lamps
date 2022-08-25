#!/usr/bin/env python
import alsaaudio
import argparse
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

lineout = alsaaudio.Mixer('Lineout')


mic2 = alsaaudio.Mixer('Mic 2')
mic2.setvolume(60)

pixel_pin = board.D12
num_pixels = 40
ORDER = neopixel.GRB
pulse_min = 60
pulse_max = 95
fade_rate = 0.005
saturation = 1.0
fading = True

neo = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

def pulse(rms):
    bottom_bright = 100 + float(rms)
    bottom_bright = constrain(bottom_bright, pulse_min, pulse_max)
    bottom_bright = mapRange(bottom_bright, pulse_min, pulse_max, 0, 255)

    if bottom_bright < 0:
        bottom_bright = 0
    if bottom_bright > 255:
        bottom_bright = 255

    writeBase(bottom_bright)

def mapRange(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def writeBulb(value):
    top_bright = value
    intensity = int(top_bright * saturation)
    for i in range(16):
        neo[i] = (intensity,intensity,intensity);
    neo.show()

def writeBase(value):
    intensity = int(value * saturation)
    for i in range(16, num_pixels):
        neo[i] = (intensity,intensity,intensity);
    neo.show()

def transition():
    top_bright = 0
    bottom_bright = 0
    fade_bulb = True
    fade_base = False
    fade_up = True
    writeBase(0)

    if top_bright < 255:
        fade_bulb = True
        fade_up = True
        fade_base = False
    elif top_bright == 255:
        fade_bulb = True
        fade_up = False
        fade_base = False

    while fading:
        if fade_bulb == True and fade_base == False:
            if fade_up:
                if top_bright < 255:
                        top_bright = top_bright + 1
                else:
                    fade_up = False
            else:
                if top_bright > 0:
                        top_bright = top_bright - 1
                else:
                    fade_bulb = False
                    fade_up = True
                    fade_base = True
            writeBulb(top_bright)
        elif fade_bulb == False and fade_base == True:
            if fade_up:
                if bottom_bright < 255:
                        bottom_bright = bottom_bright + 1
                else:
                    fade_up = False
            else:
                if bottom_bright > 0:
                        bottom_bright = bottom_bright - 1
                else:
                    fade_bulb = True
                    fade_up = True
                    fade_base = False
            writeBase(bottom_bright)
        sleep(fade_rate/10)

    while bottom_bright > 0:
        bottom_bright = bottom_bright -1
        writeBase(bottom_bright)
        sleep(fade_rate)

    while top_bright < 255:
        top_bright = top_bright + 1
        writeBulb(top_bright)
        sleep(fade_rate)


parser = argparse.ArgumentParser()
parser.add_argument('--num',
                    dest='num',
                    help='Define integers to perform addition',
                    type=int,
                    )
args = parser.parse_args()
lamp_num = args.num

class Streamer(object):
    def __init__(self):
        self.AMP_ELEMENT_NAME = 'lamp-audio-amplify'
        self.RTSP_ELEMENT_NAME = 'lamp-rtsp-source'
        self.pipeline_string = self.pipeline_template()

        self.pipeline = Gst.parse_launch(self.pipeline_string)
        self.rtspsrc = self.pipeline.get_by_name(self.RTSP_ELEMENT_NAME)
        self.audioamplify = self.pipeline.get_by_name(self.AMP_ELEMENT_NAME)
        self.volume = 0
        self.peak = 1.5

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

    def fadeIn(self, rate):
        self.volume = 0
        while self.volume < self.peak:
            self.volume = self.volume + 0.01
            self.audioamplify.set_property('amplification', self.volume)
            sleep(rate)

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
    vol = lineout.getvolume()

    print("VOLUME----------------------")
    print(vol)
    
    fader = Thread(target=transition, args=())
    fader.start()

    streamer = Streamer()
    stream_state = -1
    while stream_state == -1:
        stream_state = streamer.change(lamp_num)
        sleep(1)

    fading = False

    streamer.fadeIn(fade_rate)

    while True:
        sleep(0.01)
