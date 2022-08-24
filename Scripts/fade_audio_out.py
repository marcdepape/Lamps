import alsaaudio
from time import sleep

master = alsaaudio.Mixer('Master')
current_vol = master.getvolume()

while current_vol > 0:
    current_vol = current_vol - 1
    master.setvolume(current_vol)
    sleep(0.01)
