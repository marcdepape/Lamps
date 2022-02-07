import gi
import threading
gi.require_version('Gst', '1.0')

from gi.repository import GObject, Gst
from .audio import LampAudioStream

GObject.threads_init()
Gst.init(None)

mainloop = GObject.MainLoop()
threading.Thread(target=mainloop.run, daemon=True).start()
