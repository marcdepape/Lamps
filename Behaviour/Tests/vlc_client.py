#!/usr/bin/env python3

import vlc

def audio(source):

    instance = vlc.Instance()

    player = instance.media_player_new()

    media = instance.media_new(source)

    player.play()

audio('tcp://lamp0.local:8100')
