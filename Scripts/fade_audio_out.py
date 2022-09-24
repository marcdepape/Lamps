import alsaaudio
from time import sleep
import board
from RPi import GPIO
import neopixel

lineout = alsaaudio.Mixer('Lineout')
current_vol = int(lineout.getvolume()[0])

neo = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

value = 0

for i in range(0, num_pixels):
    neo[i] = (0,0,0)
neo.show()

while value < 255:
    for i in range(0, num_pixels):
        neo[i] = (value,value,value)
    neo.show()
    value = value + 1

while current_vol > 0:
    current_vol = current_vol - 1
    lineout.setvolume(current_vol)
    sleep(0.03)

while value > 0:
    for i in range(0, num_pixels):
        neo[i] = (value,value,value)
    neo.show()
    value = value - 1
