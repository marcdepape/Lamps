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
    lamp0_position = StringProperty()
    lamp0_ip = StringProperty()
    lamp0_log_0 = StringProperty()
    lamp0_log_1 = StringProperty()
    lamp0_log_2 = StringProperty()
    lamp0_log_3 = StringProperty()
    lamp0_log_4 = StringProperty()

    lamp1_position = StringProperty()
    lamp1_ip = StringProperty()
    lamp1_log_0 = StringProperty()
    lamp1_log_1 = StringProperty()
    lamp1_log_2 = StringProperty()
    lamp1_log_3 = StringProperty()
    lamp1_log_4 = StringProperty()

    lamp2_position = StringProperty()
    lamp2_ip = StringProperty()
    lamp2_log_0 = StringProperty()
    lamp2_log_1 = StringProperty()
    lamp2_log_2 = StringProperty()
    lamp2_log_3 = StringProperty()
    lamp2_log_4 = StringProperty()

    lamp3_position = StringProperty()
    lamp3_ip = StringProperty()
    lamp3_log_0 = StringProperty()
    lamp3_log_1 = StringProperty()
    lamp3_log_2 = StringProperty()
    lamp3_log_3 = StringProperty()
    lamp3_log_4 = StringProperty()

    lamp4_position = StringProperty()
    lamp4_ip = StringProperty()
    lamp4_log_0 = StringProperty()
    lamp4_log_1 = StringProperty()
    lamp4_log_2 = StringProperty()
    lamp4_log_3 = StringProperty()
    lamp4_log_4 = StringProperty()

    lamp5_position = StringProperty()
    lamp5_ip = StringProperty()
    lamp5_log_0 = StringProperty()
    lamp5_log_1 = StringProperty()
    lamp5_log_2 = StringProperty()
    lamp5_log_3 = StringProperty()
    lamp5_log_4 = StringProperty()

    start_time = time()
    current_time = StringProperty()
    current_peak = StringProperty()
    current_turn = StringProperty()
    current_fade = StringProperty()
    current_hue = StringProperty()
    current_saturation = StringProperty()
    current_shuffle = StringProperty()

    def __init__(self, num, **kwargs):
        super(Dashboard, self).__init__(**kwargs)

        self.number_of_lamps = num
        self.proxy = LampProxy(self.number_of_lamps)
        self.start_proxy()

        self.active_dial = False
        self.set_shuffle = 600
        self.flip_trigger = Clock.create_trigger(self.dial_flip, 30)
        self.shuffle_trigger = Clock.create_trigger(self.shuffle, self.set_shuffle)
        self.set_peak = 1.0
        self.set_fade = 3
        self.set_hue = 0
        self.set_saturation = 0

        self.listen_ids = [[0 for i in range(self.number_of_lamps)] for i in range(self.number_of_lamps)]
        self.broadcast_ids = [0 for i in range(self.number_of_lamps)]
        self.status_ids = [[0 for i in range(self.number_of_lamps)] for i in range(5)]
        self.get_ids()
        self.shuffle(0)

        Clock.schedule_interval(self.update_GUI, 0.5)
        Clock.schedule_once(self.shuffle, 10)
        Clock.schedule_once(self.shuffle, 30)
        Clock.schedule_once(self.shuffle, 60)

    def start_proxy(self):
        subscriber = Thread(target=self.proxy.statusIn, args=())
        subscriber.daemon = True
        subscriber.start()
        publisher = Thread(target=self.proxy.updateOut, args=())
        publisher.daemon = True
        publisher.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.receive)
        #print update
        lamp = update["id"]
        logs = update["console"]
        state = update["state"]

        self.current_shuffle = str(self.set_shuffle)
        self.proxy.peak = self.set_peak
        self.current_peak = str(round(self.proxy.peak,1))

        self.proxy.fade = self.set_fade
        self.current_fade = str(self.proxy.fade)
        self.proxy.hue = self.set_hue
        self.current_hue = str(self.proxy.hue)
        self.proxy.saturation = self.set_saturation
        self.current_saturation = str(self.proxy.saturation)

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.current_time = "%d:%02d:%02d" % (h, m, s)

        #self.dial_trigger(lamp, position)

        if lamp == 0:
            self.lamp0_position = str(position)
            self.lamp0_ip = "lamp0.local"

        elif lamp == 1:
            self.lamp1_position = str(position)
            self.lamp1_ip = "lamp1.local"

        elif lamp == 2:
            self.lamp2_position = str(position)
            self.lamp2_ip = "lamp2.local"

        elif lamp == 3:
            self.lamp3_position = str(position)
            self.lamp3_ip = "lamp3.local"

        elif lamp == 4:
            self.lamp4_position = str(position)
            self.lamp4_ip = "lamp4.local"

        elif lamp == 5:
            self.lamp5_position = str(position)
            self.lamp5_ip = "lamp5.local"

    def reset_lamp(self, lamp):
        if lamp != -1:
            self.proxy.exit[lamp] = 1
        else:
            for i in range(self.number_of_lamps):
                self.proxy.exit[i] = 1

    def set_peak(self, peak):
        self.proxy.peak = str(peak)
        listeners = ["x" for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assign_listeners(listeners, broadcasters)

    def all_streaming_one(self, lamp):
        self.reset_shuffle()
        listeners = []
        for i in range(self.number_of_lamps):
            if i != lamp:
                listeners.append(lamp)
            else:
                listeners.append(-1)
        self.update_button_state(listeners)

    def shuffle(self, rt):
        self.reset_shuffle()
        listeners = ["x" for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assign_listeners(listeners, broadcasters)

    def dial_trigger(self, lamp, position):
        if self.active_dial == True:
            if self.proxy.listeners[lamp] == -1 and position > 160:
                self.dial_listen(lamp)
                self.active_dial = False
            elif self.proxy.listeners[lamp] > -1 and position < 20:
                self.manual_broadcast(lamp)
                self.active_dial = False
            else:
                pass
        else:
            pass

    def dial_flip(self, rt):
        self.active_dial = True
        print ("DIAL IS ACTIVE")

    def reset_shuffle(self):
        self.active_dial = False
        self.shuffle_trigger.cancel()
        self.flip_trigger.cancel()
        self.shuffle_trigger()
        self.flip_trigger()

    def dial_listen(self, lamp):
        self.reset_shuffle()
        listeners = ["x" for i in range(self.number_of_lamps)]
        to_lamp = lamp
        while to_lamp == lamp:
            to_lamp = random.choice(range(self.number_of_lamps))
        listeners[lamp] = to_lamp
        listeners[to_lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def manual_listen(self, lamp, to_lamp):
        self.reset_shuffle()
        listeners = ["x" for i in range(self.number_of_lamps)]
        listeners[lamp] = to_lamp
        listeners[to_lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def manual_broadcast(self, lamp):
        self.reset_shuffle()
        listeners = ["x" for i in range(self.number_of_lamps)]
        listeners[lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def assign_listeners(self, listeners, broadcasters):
        print (listeners)
        broadcast_lamps = []
        while broadcasters < int(self.number_of_lamps/2):
            assignment = random.randint(0, self.number_of_lamps-1)
            if listeners[assignment] == "x":
                listeners[assignment] = -1
                broadcasters += 1
                broadcast_lamps.append(assignment)

        for i in range(self.number_of_lamps):
            if listeners[i] == "x":
                while listeners[i] == "x":
                    if not broadcast_lamps:
                        listeners[i] = assignment
                    else:
                        assignment = random.choice(broadcast_lamps)
                        listeners[i] = assignment
                        broadcast_lamps.remove(assignment)
        print ("LISTENERS {}".format(listeners))
        #self.update_button_state(listeners)

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
