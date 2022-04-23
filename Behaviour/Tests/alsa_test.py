import alsaaudio

pcms = alsaaudio.pcms()
print(pcms)
mixer = alsaaudio.Mixer()
mixer.setvolume(100)[PCM_CAPTURE]
