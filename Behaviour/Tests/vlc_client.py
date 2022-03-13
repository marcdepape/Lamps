#!/usr/bin/env python3

import vlc
import time

def audio(source):

    instance = vlc.Instance()

    player = instance.media_player_new()

    media = instance.media_new(source)

    player.set_media(media)

    player.play()

    time.sleep(10)

print("PLAY!")
audio("modular.wav")
print("STREAM!")
audio("tcp://lamp0.local:8100")
