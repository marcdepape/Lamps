#!/usr/bin/env python3

import vlc
import alsaaudio
import time

def audio(source):

    instance = vlc.Instance()

    player = instance.media_player_new()

    media = instance.media_new(source)

    player.set_media(media)

    player.play()

    time.sleep(20)

mixer = alsaaudio.Mixer()
mixer.setvolume(100)
audio("tcp://lamp0.local:8100")
