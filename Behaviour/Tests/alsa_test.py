import alsaaudio

pcms = alsaaudio.pcms("PCM_CAPTURE")
print(pcms)
mixer = alsaaudio.Mixer()
mixer.setvolume(100)["PCM_CAPTURE"]
