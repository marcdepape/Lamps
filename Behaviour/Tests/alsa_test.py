import alsaaudio

print("CARDS: {}".format(alsaaudio.cards()))
print("MIXERS: {}".format(alsaaudio.mixers()))
pcms = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)
print("PCM: {}".format(alsaaudio.PCM_CAPTURE))
print(pcms)
pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
mixer = alsaaudio.Mixer('Capture')
print(mixer.volumecap())
print("RANGE: {}".format(mixer.getrange(alsaaudio.PCM_CAPTURE)))
mixer.setvolume(65536)
