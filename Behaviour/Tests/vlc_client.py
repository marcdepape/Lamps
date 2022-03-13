#!/usr/bin/env python3

import vlc
import alsaaudio

def audio(source):

    instance = vlc.Instance()

    player = instance.media_player_new()

    media = instance.media_new(source)

    player.play()

mixer = alsaaudio.Mixer()
mixer.setvolume(100)
audio("record.wav")
