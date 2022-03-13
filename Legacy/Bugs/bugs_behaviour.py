# Bugs control program (Client, Server, Microcontroller)
from gi.repository import Gst, GObject
import gi
from time import sleep
import json
import subprocess
import sys, traceback
from threading import Thread
from multiprocessing import Queue, Pipe
from ping_all_lamps import PingLamps
from check_state import CheckState
from stream_control import LampStream
from sub_pub import LampSubPub

# RPI HOSTNAME
this_lamp = subprocess.check_output('hostname')
this_lamp = int(this_lamp.replace("lamp","",1))

# PING OTHER LAMPS
ping_all = PingLamps(this_lamp)

# CHECK ATMEGA
check_lamp = CheckState()
lamp_state = "..."

# INITIALIZE STREAMING
GObject.threads_init()
Gst.init(None)

mainloop = GObject.MainLoop()
m = Thread(name="mainloop", target=mainloop.run)
m.daemon = True
m.start()

# START SUB PUB
lamp_update = LampSubPub(this_lamp)

def setup(check_lamp):
    print "SETING UP LAMPS..."

    while True:
        intro = lamp_update.receive()

        if intro != -1:
            if intro["live"] == 1 and check_lamp.atmega_ready == True:
                ping_all.update(intro["ip"])
                print "ALL LAMPS READY!"
                return intro
        else:
            pass

class ConsoleLog(object):
    def __init__(self):
        self.stream = None
        self.log = ["","","","",""]
        self.console_update = True

    def set(self, stream):
        self.stream = stream

    def message(self, msg):
        if self.stream != None:
            self.stream.status(msg)
        else:
            update = []
            update.append(msg)
            for i in range(0, len(self.log)-1):
                update.append(str(self.log[i]))
            self.log = update

    def console(self, q):
        q.put("...")
        while True:
            ready = q.get()
            if ready == "READY":
                if self.stream != None and self.console_update == True:
                    self.log = self.stream.status("GET")
                elif self.stream == None and self.console_update == True:
                    self.message("LIVE!")
                    self.console_update = False
                elif self.stream != None and self.console_update == False:
                    self.console_update = True
                    self.stream.log = self.log
                else:
                    pass
            else:
                pass
            q.put(self.log)

monitor = ConsoleLog()

#---------------------------------------------------------------------------------------------
# THREADS
q = Queue()
p = Thread(name='ping_all_other_lamps', target=ping_all.forever)
l = Thread(name='check_lamp_atmega', target=check_lamp.forever)
s = Thread(name='lamp_server', target=lamp_update.send, args=(q,))
c = Thread(name='console', target=monitor.console, args=(q,))

# SET THREADS
p.daemon = True
l.daemon = True
s.daemon = True
c.daemon = True

if __name__ == '__main__':
    p.start()
    l.start()
    s.start()
    c.start()
    sleep(3)

    old = setup(check_lamp)

    # LAMP STREAM
    this_stream = LampStream(old["rate"], old["peak"])
    if old["listen"] != -1:
        l = Thread(target=this_stream.start_stream, args=(old["ip"][old["listen"]],))
        l.daemon = True
        l.start()
    else:
        this_stream = None

    while True:
        new = lamp_update.receive()
        if new != -1:
            if new["exit"] == 1:
                subprocess.Popen(('sudo', 'reboot', 'now'), stdout=subprocess.PIPE)

            if new["parameters"] != old["parameters"]:
                parameters = new["parameters"]
                if parameters[0] != check_lamp.turn:
                    check_lamp.update('t', parameters[0])
                if parameters[1] != check_lamp.fade:
                    check_lamp.update('f', parameters[1])
                if parameters[2] != check_lamp.hue:
                    check_lamp.update('h', parameters[2])
                if parameters[3] != check_lamp.saturation:
                    check_lamp.update('s', parameters[3])

            if lamp_state != check_lamp.state and len(check_lamp.state) == 2:
                lamp_state = check_lamp.state
                monitor.message("{}: {}".format(lamp_state[0],lamp_state[1]))

            if new["listen"] != old["listen"]:
                if new["listen"] != -1 and old["listen"] != -1:
                    # c = change lamps
                    check_lamp.update('c',0)
                    this_stream.stop_stream()
                    this_stream = None
                    this_stream = LampStream(new["rate"], new["peak"])
                    l = Thread(target=this_stream.start_stream, args=(new["ip"][new["listen"]],))
                    l.daemon = True
                    l.start()
                    monitor.set(this_stream)
                    monitor.message("LISTEN TO {}".format(new["listen"]))
                elif new["listen"] != -1 and old["listen"] == -1:
                    # l = listen
                    check_lamp.update('l',0)
                    this_stream = LampStream(new["rate"], new["peak"])
                    l = Thread(target=this_stream.start_stream, args=(new["ip"][new["listen"]],))
                    l.daemon = True
                    l.start()
                    monitor.set(this_stream)
                    monitor.message("SWITCH TO {}".format(new["listen"]))
                elif new["listen"] == -1:
                    # b = broadcast mode
                    check_lamp.update('b',0)
                    monitor.message("BROADCAST")
                    this_stream.stop_stream()
                    this_stream = None
                    monitor.set(this_stream)
                else:
                    pass
            lamp_update.position = check_lamp.position
            old = new
