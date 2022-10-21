from motor import *
import RPi.GPIO as GPIO


class LineTracking:
    def __init__(self):
        self.IR01 = 14
        self.IR02 = 15
        self.IR03 = 23
        self.LMR = 0x00
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR01, GPIO.IN)
        GPIO.setup(self.IR02, GPIO.IN)
        GPIO.setup(self.IR03, GPIO.IN)
        self.motor = Motor()

    def run(self):
        while True:
            self.LMR = 0x00
            if GPIO.input(self.IR01):
                self.LMR = (self.LMR | 4)
            if GPIO.input(self.IR02):
                self.LMR = (self.LMR | 2)
            if GPIO.input(self.IR03):
                self.LMR = (self.LMR | 1)
            if self.LMR == 2:
                self.motor.set_speed(800, 800, 800, 800)
            elif self.LMR == 4:
                self.motor.set_speed(-1500, -1500, 2500, 2500)
            elif self.LMR == 6:
                self.motor.set_speed(-2000, -2000, 4000, 4000)
            elif self.LMR == 1:
                self.motor.set_speed(2500, 2500, -1500, -1500)
            elif self.LMR == 3:
                self.motor.set_speed(4000, 4000, -2000, -2000)
            elif self.LMR == 7:
                # pass
                self.motor.set_speed(0, 0, 0, 0)

    def destroy(self):
        self.motor.set_speed(0, 0, 0, 0)


def main():
    print('Program is starting ... ')
    line_tracking = LineTracking()
    try:
        line_tracking.run()
    except KeyboardInterrupt:
        line_tracking.destroy()


if __name__ == '__main__':
    main()
