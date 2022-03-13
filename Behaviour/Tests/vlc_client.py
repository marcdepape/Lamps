#!/usr/bin/env python3

import vlc
import alsaaudio
import time

def audio(source):

    instance = vlc.Instance()

    player = instance.media_player_new()

    media = instance.media_new(source)

    player.play()

    value = player.audio_output_device_enum()
    print(value)
    time.sleep(30)

mixer = alsaaudio.Mixer()
mixer.setvolume(100)
audio("record.wav")
