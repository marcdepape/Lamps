#!/usr/bin/env python
import zmq
import json
from RPi import GPIO
import board
import neopixel
from time import sleep
from threading import Thread

class Lamp(object):
    def __init__(self):
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

    #mic = Thread(target=lamp.micLevels, args=())
    #mic.start()

    while True:
        lamp.micLevels()
        sleep(0.01)
