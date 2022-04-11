from RPi import GPIO
from time import sleep

btn = 16
clk = 24
dt = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 0
clkLastState = GPIO.input(clk)
btnLastState = GPIO.input(btn)

try:
        while True:
                clkState = GPIO.input(clk)
                dtState = GPIO.input(dt)
                btnState = GPIO.input(btn)

                if clkState != clkLastState:
                        if dtState != clkState:
                                counter += 1
                        else:
                                counter -= 1
                        print("BTN: {} | COUNT: {} | CLK: {} | DT: {}".format(btnState, counter, clkState, dtState))

                if btnState != btnLastState:
                    print("BTN: {} | CLK: {} | DT: {}".format(btnState, clkState, dtState))

                clkLastState = clkState
                btnLastState = btnState

                sleep(0.001)
finally:
        GPIO.cleanup()

'''
def encoder(self):
    clk_state = GPIO.input(self.clk)
    dt_state = GPIO.input(self.dt)
    #btn_state = GPIO.input(self.btn)

    increment = 4
    self.counter += 1

    if clk_state != self.last_clk:
        counter = 0
        if dt_state != clk_state:
            if self.bottom_rotation > 0:
                self.bottom_rotation -= increment
                if self.bottom_rotation < 0:
                    self.bottom_rotation = 0
            elif self.top_rotation < 255:
                self.top_rotation += increment
                if self.top_rotation > 255:
                    self.top_rotation = 255
        else:
            if self.top_rotation > 0:
                self.top_rotation -= increment
                if self.top_rotation < 0:
                    self.top_rotation = 0
            elif self.bottom_rotation < 255:
                self.bottom_rotation += increment
                if self.bottom_rotation > 255:
                    self.bottom_rotation = 255

        self.writeBulb(self.top_rotation,)
        self.writeBase(self.bottom_rotation)

        if self.top_rotation > 150 and self.command != "listen":
            print("MANUAL LISTEN!")
            self.command = "listen"
        elif self.bottom_rotation > 150 and self.command != "broadcast":
            print("MANUAL BROADCAST!")
            self.command = "broadcast"

    self.last_clk = clk_state
    #self.last_btn = btn_state

    if self.counter > 20:
        if self.top_rotation > 0 and self.command != "listen":
            self.top_rotation -= 1
            self.writeBulb(self.top_rotation)
            self.writeBase(self.bottom_rotation)
        if self.bottom_rotation > 0 and self.command != "broadcast":
            self.bottom_rotation -= 1
            self.writeBulb(self.top_rotation)
            self.writeBase(self.bottom_rotation)
        self.counter = 0
'''
