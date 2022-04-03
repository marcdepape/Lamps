#!/usr/bin/env python3
import sys
import zmq
import gi

gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GObject, GLib

context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_socket.bind("tcp://127.0.0.1:8103")
zmq_socket.set_hwm(1)

def message_callback(bus, message):
    if message.type == Gst.MessageType.ELEMENT:
        structure = message.get_structure()
        name = structure.get_name()

        if name == "level":
            value = structure.get_value("rms")
            value = value[0]
            print(value)
            zmq_socket.send_string(str(value))

if __name__ == "__main__":
    Gst.init(None)

    print("LAUNCH LAMP AUDIO LEVEL!")

    pipeline = Gst.parse_launch(
        "alsasrc ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! level name=wavelevel interval=100000000 post-messages=TRUE ! fakesink"
    )

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", message_callback)

    pipeline.set_state(Gst.State.PLAYING)
    GLib.MainLoop().run()
    pipeline.set_state(Gst.State.NULL)
