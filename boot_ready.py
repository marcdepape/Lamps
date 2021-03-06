# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import board
import neopixel
import os
from time import sleep
import subprocess

this_lamp = subprocess.check_output('hostname')
this_lamp = this_lamp.decode("utf-8")
this_lamp = this_lamp.replace('lamp','',1)
lamp_id = int(this_lamp)

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D12

# The number of NeoPixels
num_pixels = 40

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

neo = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

for i in range(0, 16):
    neo[i] = (0,255,0);
    neo.show()

for i in range(16, 40):
    neo[i] = (0,0,0);
    neo.show()

while True:
    response = os.system("ping -c 1 downy.local")
    if response == 0:
        print("LAMP {} IS PINGED!".format(lamp_id))
        sleep(10)
    else:
        print("LAMP {} IS PINGING...".format(lamp_id))
        sleep(1)
