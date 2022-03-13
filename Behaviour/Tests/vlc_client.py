#!/usr/bin/env python3

import VLC

Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new('tcp://lamp1.local:8100')
player.play()
