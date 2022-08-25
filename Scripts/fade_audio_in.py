import alsaaudio
from time import sleep

lineout = alsaaudio.Mixer('Lineout')
current_vol = int(lineout.getvolume()[0])

while current_vol < 95:
    current_vol = current_vol + 1
    lineout.setvolume(current_vol)
    sleep(0.03)
