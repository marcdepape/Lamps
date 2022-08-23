#!/usr/bin/env python
from RPi import GPIO
import board
import neopixel
import subprocess
from time import sleep

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
print("THIS LAMP IS LAMP NUMBER: " + this_lamp)
lamp_id = int(this_lamp)

class Lamp(object):
    def __init__(self):
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.top_bright = 0
        self.bottom_bright = 0

        # NeoPixel
        self.pixel_pin = board.D12
        self.num_pixels = 40
        self.neo = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB
        )
        self.setOff()

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

lamp = Lamp()
lamp.writeBase(0)

lamp.top_bright = 255

while lamp.top_bright > 0:
    lamp.changeBulb(-1)
    sleep(lamp.fade_rate)

#fade audio here
