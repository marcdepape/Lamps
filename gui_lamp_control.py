#!/usr/bin/env python
import zmq
import json
import random
import os
from time import sleep, process_time, time, strftime
from threading import Thread
from gui_sub_pub import LampProxy

# KIVY setup
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp2.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp3.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp4.local sudo ./launch.sh &")
#os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp5.local sudo ./launch.sh &")


#-------------------------------------------------------------------------------------------------------------
# kivy

class Dashboard(GridLayout):
    start_time = time()
    display_time = StringProperty()
    display_peak = StringProperty()
    display_fade_rate = StringProperty()
    display_saturation = StringProperty()
    display_shuffle = StringProperty()

    display_console_0 = StringProperty()
    display_console_1 = StringProperty()
    display_console_2 = StringProperty()
    display_console_3 = StringProperty()
    display_console_4 = StringProperty()
    display_console_5 = StringProperty()

    display_connection_0 = StringProperty()
    display_connection_1 = StringProperty()
    display_connection_2 = StringProperty()
    display_connection_3 = StringProperty()
    display_connection_4 = StringProperty()
    display_connection_5 = StringProperty()

    def __init__(self, num, **kwargs):
        super(Dashboard, self).__init__(**kwargs)



        self.number_of_lamps = num
        self.proxy = LampProxy(self.number_of_lamps)
        self.inbound = None
        self.start_proxy()

        self.shuffle_time = 60

        self.shuffle_trigger = Clock.create_trigger(self.shuffle, self.shuffle_time)

        self.display_connection_0 = ""
        self.display_connection_1 = ""
        self.display_connection_2 = ""
        self.display_connection_3 = ""
        self.display_connection_4 = ""
        self.display_connection_5 = ""

        self.peak = 1.5
        self.fade_rate = 0.05
        self.saturation = 1.0
        self.unassigned = 255

        self.proxy.peak = self.peak
        self.proxy.fade_rate = self.fade_rate
        self.proxy.saturation = self.saturation

        self.display_shuffle = str(self.shuffle_time)
        self.display_peak = str(self.peak)
        self.display_fade_rate = str(self.fade_rate)
        self.display_saturation = str(self.saturation)

        self.connection_times = [0 for i in range(self.number_of_lamps)]
        self.listen_ids = [[0 for i in range(self.number_of_lamps)] for i in range(self.number_of_lamps)]
        self.broadcast_ids = [0 for i in range(self.number_of_lamps)]
        self.status_ids = [[0 for i in range(self.number_of_lamps)] for i in range(5)]
        self.get_ids()
        self.shuffle(0)

        for i in range(self.number_of_lamps):
            self.proxy.command[i] = "start"

        Clock.schedule_interval(self.update_GUI, 0.1)

    def start_proxy(self):
        subscriber = Thread(target=self.proxy.statusIn, args=())
        subscriber.daemon = True
        subscriber.start()
        publisher = Thread(target=self.proxy.updateOut, args=())
        publisher.daemon = True
        publisher.start()

    def update_GUI(self, rt):
        update = None
        lamp = None
        state = None

        update = json.loads(self.proxy.receive)
        if update != self.inbound:
            self.inbound = update
            lamp = update["id"]
            state = update["state"]
            if lamp >=0:
                self.proxy.command[lamp] = update["command"]
        else:
            lamp = -1

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.display_time = "%d:%02d:%02d" % (h, m, s)

        for i in range(self.number_of_lamps):
            self.connection_times[i]+=1

        if lamp >= 0:
            if update["command"] == "listen":
                self.manualListen(lamp, -1)
                self.proxy.command[lamp] = "complete"
            elif update["command"] == "broadcast":
                self.manualBroadcast(lamp)
                self.proxy.command[lamp] = "complete"

            if update["state"] == "error":
                if update['stream'] > 0:
                    self.reset(update['stream'])

        if lamp == 0:
            self.display_console_0 = update["console"]
            self.display_connection_0 = "CONNECTED"
            self.connection_times[0] = 0

        elif lamp == 1:
            self.display_console_1 = update["console"]
            self.display_connection_1 = "CONNECTED"
            self.connection_times[1] = 0

        elif lamp == 2:
            self.display_console_2 = update["console"]
            self.display_connection_2 = "CONNECTED"
            self.connection_times[2] = 0

        elif lamp == 3:
            self.display_console_3 = update["console"]
            self.display_connection_3 = "CONNECTED"
            self.connection_times[3] = 0

        elif lamp == 4:
            self.display_console_4 = update["console"]
            self.display_connection_4 = "CONNECTED"
            self.connection_times[4] = 0

        elif lamp == 5:
            self.display_console_5 = update["console"]
            self.display_connection_5 = "CONNECTED"
            self.connection_times[5] = 0

        pings = 100
        if self.connection_times[0] > pings:
            self.display_connection_0 = "OFFLINE"
        if self.connection_times[1] > pings:
            self.display_connection_1 = "OFFLINE"
        if self.connection_times[2] > pings:
            self.display_connection_2 = "OFFLINE"
        if self.connection_times[3] > pings:
            self.display_connection_3 = "OFFLINE"
        if self.connection_times[4] > pings:
            self.display_connection_4 = "OFFLINE"
        if self.connection_times[5] > pings:
            self.display_connection_5 = "OFFLINE"

    def reset(self, lamp):
        if lamp != -1:
            #self.proxy.command[lamp] = "reboot"
            os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp{}.local sudo ./launch.sh &".format(lamp))

        else:
            for i in range(self.number_of_lamps):
                #self.proxy.command[i] = "reboot"
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp0.local sudo ./launch.sh &")
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp1.local sudo ./launch.sh &")
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp2.local sudo ./launch.sh &")
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp3.local sudo ./launch.sh &")
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp4.local sudo ./launch.sh &")
                os.system("sshpass -p \'marcdepape\' ssh -o StrictHostKeyChecking=no pi@lamp5.local sudo ./launch.sh &")


    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def setShuffleTime(self, change):
        self.shuffle_time = self.constrain(self.shuffle_time + change, 30, 1200)
        self.display_shuffle = str(self.shuffle_time)

    def setFadeRate(self, change):
        self.fade_rate = self.constrain(self.fade_rate + change, 0.01, 1.00)
        self.proxy.fade_rate = self.fade_rate
        self.display_fade_rate = "{:.2f}".format(self.fade_rate)

    def setPeak(self, change):
        self.peak = self.constrain(self.peak + change, 0.10, 2.00)
        self.proxy.peak = self.peak
        self.display_peak = "{:.2f}".format(self.peak)

    def setSaturation(self, change):
        self.saturation = self.constrain(self.saturation + change, 0.00, 1.0)
        self.proxy.saturation = self.saturation
        self.display_saturation = "{:.2f}".format(self.saturation)

    def allStreamingOne(self, lamp):
        self.resetShuffle()
        listeners = []
        for i in range(self.number_of_lamps):
            if i != lamp:
                listeners.append(lamp)
            else:
                listeners.append(-1)
        self.update_button_state(listeners)

    def shuffle(self, rt):
        print("SHUFFLE!")
        self.resetShuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assignListeners(listeners, broadcasters)

    def resetShuffle(self):
        self.shuffle_trigger.cancel()
        self.shuffle_trigger()

    def manualListen(self, lamp, to_lamp):
        print("MANUAL LISTEN! " + str(lamp) + " : " + str(to_lamp))
        self.resetShuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        broadcasters = 0
        if to_lamp != -1:
            listeners[lamp] = to_lamp
            listeners[to_lamp] = -1
            broadcasters = 1
        else:
            assignment = lamp
            while assignment == lamp:
                assignment = random.randint(0, self.number_of_lamps-1)
                listeners[lamp] = assignment
                listeners[assignment] = -1
                broadcasters = 1
        self.assignListeners(listeners, broadcasters)

    def manualBroadcast(self, lamp):
        print("MANUAL BROADCAST! " + str(lamp))
        self.resetShuffle()
        listeners = [self.unassigned for i in range(self.number_of_lamps)]
        listeners[lamp] = -1
        broadcasters = 1
        self.assignListeners(listeners, broadcasters)

    def assignListeners(self, listeners, broadcasters):
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
