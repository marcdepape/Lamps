import alsaaudio

pcms = alsaaudio.pcms()
print(pcms)
mixer = alsaaudio.Mixer()
mixer.setvolume(100)[pcms.PCM_CAPTURE]
