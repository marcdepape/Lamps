from time import sleep
import serial

class CheckStatus(object):
    def __init__(self):
        self.running = True
        self.atmega_ready = False
        self.listen = 0
        self.position = 0
        self.read = True
        self.cmd = 'r'
        self.value = 0
        self.status = ""
        self.turn = 2
        self.fade = 2
        self.hue = 0
        self.saturation = 0
        self.atmega = serial.Serial('/dev/ttyAMA0', 57600)

    def command(self, cmd, value):
        self.atmega.flushInput()
        for letter in (cmd + str(value)):
            self.atmega.write(bytes(letter.encode('ascii')))
            #sleep(0.01)
        try:
            lamp_status = self.atmega.readline()
            #self.atmega.flushInput()
        except Exception as e:
            self.atmega.flushInput()
            return False
        lamp_status = lamp_status.rstrip()
        lamp_values = lamp_status.split(":",2)
        self.status = lamp_values
        if cmd != 'r':
            print self.status
        if cmd == 'r' and lamp_values[0] == "READ":
            self.position = int(lamp_values[1])
            return True
        elif cmd == 'c' and lamp_values[0] == "CHANGE":
            print "CHANGE: TRUE"
            return True
        elif cmd == 'l' and lamp_values[0] == "LISTEN":
            print "LISTEN: TRUE"
            return True
        elif cmd == 'b' and lamp_values[0] == "BROADCAST":
            print "BROADCAST: TRUE"
            return True
        elif cmd == 't' and lamp_values[0] == "TURN":
            if int(lamp_values[1]) == value:
                self.turn = int(lamp_values[1])
                return True
            else:
                return False
        elif cmd == 'f' and lamp_values[0] == "FADE":
            if int(lamp_values[1]) == value:
                self.fade = int(lamp_values[1])
                return True
            else:
                return False
        elif cmd == 'h' and lamp_values[0] == "HUE":
            if int(lamp_values[1]) == value:
                self.hue = int(lamp_values[1])
                return True
            else:
                return False
        elif cmd == 's' and lamp_values[0] == "SATURATION":
            if int(lamp_values[1]) == value:
                self.saturation = int(lamp_values[1])
                return True
            else:
                return False
        elif lamp_values[0] == "ERROR":
            return False
        else:
            print "{}: FALSE".format(cmd)
            return False

    def update(self, cmd, value):
        #print cmd
        self.read = False
        sleep(0.1)
        while self.read == False:
            #print "WAITING: {}".format(self.read)
            self.read = self.command(cmd, value)
            sleep(0.1)

    def stop(self):
        self.running = False

    def forever(self):
        self.running = True
        while self.atmega_ready == False:
            sleep(5)
            self.atmega_ready = self.command('r', 0)
        while self.running == True:
            sleep(0.1)
            if self.read == True:
                self.command('r', 0)
            else:
                pass
