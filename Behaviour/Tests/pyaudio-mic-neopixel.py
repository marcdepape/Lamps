import pyaudio
import time
import board
import neopixel
import numpy as np

pixel_pin = board.D12
num_pixels = 32
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

CHUNK = 2**11
RATE = 44100

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

p=pyaudio.PyAudio()

stream=p.open(format=pyaudio.paInt16,
                input_device_index=0,
                channels=1,rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

for i in range(int(10*44100/1024)): #go for a few seconds
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    peak=int(np.clip(np.average(np.abs(data))/3,0,255))
    if peak < 30:
        peak = 0
    for i in range(num_pixels):
        pixels[i] = (peak,peak,peak);
    pixels.show()
    print(peak)

stream.stop_stream()
stream.close()
p.terminate()
