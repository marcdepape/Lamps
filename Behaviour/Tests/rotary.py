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
                        print(counter)

                if btnState != btnLastState:
                    print(btnState)

                clkLastState = clkState
                btnLastState = btnState

                sleep(0.01)
finally:
        GPIO.cleanup()
