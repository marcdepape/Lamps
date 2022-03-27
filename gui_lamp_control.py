#!/usr/bin/env python
import zmq
import json
import random
from time import sleep, process_time, time, strftime
from threading import Thread
from lamps_sub_pub import LampProxy

# KIVY setup
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

#-------------------------------------------------------------------------------------------------------------
# kivy

class Dashboard(GridLayout):
    start_time = time()
    display_time = StringProperty()
    display_peak = StringProperty()
    display_rate = StringProperty()
    display_fade = StringProperty()
    display_hue = StringProperty()
    display_saturation = StringProperty()
    display_shuffle = StringProperty()

    display_console_0 = StringProperty()
    display_console_1 = StringProperty()
    display_console_2 = StringProperty()
    display_console_3 = StringProperty()
    display_console_4 = StringProperty()
    display_console_5 = StringProperty()

    def __init__(self, num, **kwargs):
        super(Dashboard, self).__init__(**kwargs)

        self.number_of_lamps = num
        self.proxy = LampProxy(self.number_of_lamps)
        self.start_proxy()

        self.shuffle = 60
        self.shuffle_trigger = Clock.create_trigger(self.shuffle, self.shuffle)
        self.peak = 1.0
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.unassigned = 255
        self.state = "Launching..."

        self.proxy.peak = self.peak
        self.proxy.fade_rate = self.fade_rate
        self.proxy.saturation = self.saturation

        self.listen_ids = [[0 for i in range(self.number_of_lamps)] for i in range(self.number_of_lamps)]
        self.broadcast_ids = [0 for i in range(self.number_of_lamps)]
        self.status_ids = [[0 for i in range(self.number_of_lamps)] for i in range(5)]
        self.get_ids()
        self.shuffle(0)

        Clock.schedule_interval(self.update_GUI, 0.1)
        Clock.schedule_once(self.shuffle, 30)

    def start_proxy(self):
        subscriber = Thread(target=self.proxy.statusIn, args=())
        subscriber.daemon = True
        subscriber.start()
        publisher = Thread(target=self.proxy.updateOut, args=())
        publisher.daemon = True
        publisher.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.receive)
        lamp = update["id"]
        logs = update["console"]
        state = update["state"]

        self.display_shuffle = str(self.shuffle)

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.display_time = "%d:%02d:%02d" % (h, m, s)

        if lamp == 0:
            self.display_console_0 = logs[0]

        elif lamp == 1:
            self.display_console_1 = logs[1]

        elif lamp == 2:
            self.display_console_2 = logs[2]

        elif lamp == 3:
            self.display_console_3 = logs[3]

        elif lamp == 4:
            self.display_console_4 = logs[4]

        elif lamp == 5:
            self.display_console_5 = logs[5]

    def reset(self, lamp):
        if lamp != -1:
            self.proxy.exit[lamp] = 1
        else:
            for i in range(self.number_of_lamps):
                self.proxy.exit[i] = 1

    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def setFadeRate(self, change):
        self.fade_rate = self.constrain(self.fade_rate + change, 0.01, 1.00)
        self.proxy.fade_rate = self.fade_rate
        self.display_fade = str(self.fade_rate)

    def setPeak(self, change):
        self.peak = self.constrain(self.peak + change, 0.10, 2.00)
        self.proxy.peak = self.peak
        self.display_peak = str(self.peak)

    def setSaturation(self, change):
        self.saturation = self.constrain(self.saturation + change, 0.00, 1.0)
        self.proxy.saturation = self.saturation
        self.display_saturation = str(self.saturation)

    def all_streaming_one(self, lamp):
        self.reshuffle()
        listeners = []
        for i in range(self.number_of_lamps):
            if i != lamp:
                listeners.append(lamp)
            else:
                listeners.append(-1)
        self.update_button_state(listeners)

    def shuffle(self, rt):
        self.reshuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assign_listeners(listeners, broadcasters)

    def reshuffle(self):
        self.shuffle_trigger.cancel()
        self.shuffle_trigger()

    def manual_listen(self, lamp, to_lamp):
        self.reshuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        listeners[lamp] = to_lamp
        listeners[to_lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def manual_broadcast(self, lamp):
        self.reshuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        listeners[lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def assign_listeners(self, listeners, broadcasters):
        print (str(listeners) + " | " + str(broadcasters))
        broadcast_lamps = []
        while broadcasters < int(self.number_of_lamps/2):
            assignment = random.randint(0, self.number_of_lamps-1)
            if listeners[assignment] == self.unassigned:
                listeners[assignment] = -1
                broadcasters += 1
                broadcast_lamps.append(assignment)

        for i in range(self.number_of_lamps):
            if listeners[i] == self.unassigned:
                while listeners[i] == self.unassigned:
                    if not broadcast_lamps:
                        listeners[i] = assignment
                    else:
                        assignment = random.choice(broadcast_lamps)
                        listeners[i] = assignment
                        broadcast_lamps.remove(assignment)
        print ("LISTENERS {}".format(listeners))
        self.update_button_state(listeners)

    def update_button_state(self, listeners):
        for i in range(self.number_of_lamps):
            self.broadcast_ids[i].state = "normal"
            for j in range(self.number_of_lamps):
                self.listen_ids[i][j].state = "normal"

        for i in range(self.number_of_lamps):
            if listeners[i] == -1:
                self.broadcast_ids[i].state = "down"
            else:
                self.listen_ids[i][listeners[i]].state = "down"

        print (listeners)
        self.proxy.listeners = listeners

    def get_ids(self):
        i = 0
        for key in self.ids.items():
            this_id = str(key[0]).split("_")
            if this_id[0] == "listen":
                self.listen_ids[int(this_id[1])][int(this_id[3])] = key[1]
            if this_id[0] == "broadcast":
                self.broadcast_ids[int(this_id[1])] = key[1]
            if this_id[0] == "status":
                self.status_ids[int(this_id[1])][int(this_id[3])] = key[1]


class guiApp(App):
    def build(self):
        return Dashboard(6)

if __name__ == "__main__":
    guiApp().run()
