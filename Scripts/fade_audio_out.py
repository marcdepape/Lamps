import alsaaudio
from time import sleep

while current_vol > 0:
    current_vol = current_vol - 1
    lineout.setvolume(current_vol)
    sleep(0.03)
