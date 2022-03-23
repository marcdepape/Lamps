#!/usr/bin/env python3
import sys

import gi

gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GObject, GLib

#pipeline = None
#bus = None
#message = None

def message_callback(bus, message):
    print(message)

    if message.type == Gst.MessageType.ELEMENT:
        structure = message.get_structure()
        name = structure.get_name()
        print(name)

        if name == "level":
            value = structure.get_value("rms")
            value = value[0]
            print(100 + value)

if __name__ == "__main__":
    Gst.init(None)

    pipeline = Gst.parse_launch(
        "filesrc location=05Arrows.ogg ! oggdemux ! queue ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! level name=wavelevel interval=10000000 post-messages=TRUE ! alsasink name=output"
    )

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", message_callback)

    pipeline.set_state(Gst.State.PLAYING)
    GLib.MainLoop().run()
    pipeline.set_state(Gst.State.NULL)
