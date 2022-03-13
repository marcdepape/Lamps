from time import sleep
import serial

class CheckState(object):
    def __init__(self):
        self.running = True
        self.atmega_ready = False
        self.listen = 0
        self.position = 0
        self.read = True
        self.cmd = 'p'
        self.value = 0
        self.state = ""
        self.turn = 2
        self.fade = 2
        self.hue = 0
        self.saturation = 0
        self.atmega = serial.Serial('/dev/ttyAMA0', 9600)

    def command(self, cmd, value):
        self.atmega.flushInput()
        send = cmd + str(value)
        for letter in (send):
            self.atmega.write(bytes(letter.encode('ascii')))
            #sleep(0.01)
        try:
            lamp_state = self.atmega.readline()
            #self.atmega.flushInput()
        except Exception as e:
            self.atmega.flushInput()
            return False
        lamp_state = lamp_state.rstrip()
        lamp_values = lamp_state.split(":",2)

        try:
            lamp_values[1] = int(lamp_values[1])
        except Exception as e:
            #print "e: {}".format(e)
            return False

        if cmd == 'p' and lamp_values[0] == "READ":
            #print "READ: TRUE"
            self.position = lamp_values[1]
            return True
        elif cmd == 'c' and lamp_values[0] == "CHANGE":
            print "c: TRUE"
            self.state = lamp_values
            return True
        elif cmd == 'l' and lamp_values[0] == "LISTEN":
            print "l: TRUE"
            self.state = lamp_values
            return True
        elif cmd == 'b' and lamp_values[0] == "BROADCAST":
            print "b: TRUE"
            self.state = lamp_values
            return True
        elif cmd == 't' and lamp_values[0] == "TURN":
            if lamp_values[1] == value:
                print "t: TRUE"
                self.turn = lamp_values[1]
                self.state = lamp_values
                return True
            else:
                return False
        elif cmd == 'f' and lamp_values[0] == "FADE":
            if lamp_values[1] == value:
                print "f: TRUE"
                self.fade = lamp_values[1]
                self.state = lamp_values
                return True
            else:
                return False
        elif cmd == 'h' and lamp_values[0] == "HUE":
            if lamp_values[1] == value:
                print "h: TRUE"
                self.hue = lamp_values[1]
                self.state = lamp_values
                return True
            else:
                return False
        elif cmd == 's' and lamp_values[0] == "SATURATION":
            if lamp_values[1] == value:
                print "s: TRUE"
                self.saturation = lamp_values[1]
                self.state = lamp_values
                return True
            else:
                return False
        elif lamp_values[0] == "ERROR":
            return False
        else:
            #print "{}: False".format(cmd)
            self.state = lamp_values
            return False

    def update(self, cmd, value):
        self.read = False
        sleep(0.25)
        while self.read == False:
            print "{}: {}".format(cmd, self.read)
            self.read = self.command(cmd, value)
            sleep(0.1)

    def stop(self):
        self.running = False

    def forever(self):
        self.running = True
        sleep(5)
        while self.atmega_ready == False:
            sleep(0.25)
            self.atmega_ready = self.command('p', 0)
        print "ATMEGA READY!"
        while self.running == True:
            sleep(0.25)
            if self.read == True:
                self.command('p', 0)
            else:
                pass
