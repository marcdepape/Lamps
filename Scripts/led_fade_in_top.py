from time import sleep
import board
from RPi import GPIO
import neopixel
pixel_pin = board.D12
num_pixels = 40
ORDER = neopixel.GRB

neo = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

top_bright = 0

def writeBulb(value):
    for i in range(16):
        neo[i] = (value,value,value);
    neo.show()

def writeBase(value):
    for i in range(16, num_pixels):
        neo[i] = (value,value,value)
    neo.show()

if __name__ == '__main__':
    while top_bright < 255:
        writeBulb(top_bright)
        top_bright = top_bright + 1
        sleep(0.01)
