from adc import *
from motor import *


class Light:
    def __init__(self, adc):
        self.motor = Motor()
        self.adc = adc

    def run(self):
        try:
            self.motor.set_speed(0, 0, 0, 0)
            while True:
                left = self.adc.recv(0)
                right = self.adc.recv(1)
                if left < 2.99 and right < 2.99:
                    self.motor.set_speed(600, 600, 600, 600)

                elif abs(left - right) < 0.15:
                    self.motor.set_speed(0, 0, 0, 0)

                elif left > 3 or right > 3:
                    if left > right:
                        self.motor.set_speed(-1200, -1200, 1400, 1400)

                    elif right > left:
                        self.motor.set_speed(1400, 1400, -1200, -1200)

        except KeyboardInterrupt:
            self.motor.set_speed(0, 0, 0, 0)


def main():
    print('Program is starting ... ')
    adc = ADC()
    led_car = Light(adc)
    led_car.run()


if __name__ == '__main__':
    main()
