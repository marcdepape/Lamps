import alsaaudio

pcms = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)
print(pcms)
mixer = alsaaudio.Mixer()
mixer.setvolume(100)[alsaaudio.PCM_CAPTURE]
