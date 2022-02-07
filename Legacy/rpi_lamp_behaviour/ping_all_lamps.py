from time import sleep
import subprocess
import threading

class PingLamps(object):
    def __init__(self, this_lamp):
        self.this_lamp = this_lamp
        self.addresses = [-1,-1,-1,-1]
        self.running = True
        self.t = ""

    def keep_live(self):
        #print "PING_ALL: " + str(self.addresses)
        for ping in range(0,len(self.addresses)):
            if ping != self.this_lamp:
                if self.addresses[ping] != -1:
                    check = True
                    while check:
                        try:
                            res = subprocess.check_output(['sudo','ping','-q','-c','1', self.addresses[ping]],universal_newlines=True)
                            res = res.split(",")
                            res = res[1].split(" ")
                            status = res[1]
                            status = int(status)
                            #print "ping to Lamp" + str(ping + 1), self.addresses[ping], "OK"
                            check = False
                        except subprocess.CalledProcessError as e:
                            #print "no response from Lamp" + str(ping + 1), self.addresses[ping]
                            check = True

    def stop(self):
        self.running = False

    def update(self, addresses):
        self.addresses = addresses

    def forever(self):
        self.running = True
        while self.running == True:
            self.keep_live()
            sleep(2)
