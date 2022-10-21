import sys
import time

from RPi import GPIO

from adc import ADC
from buzzer import Buzzer
from led import Led
from line_tracking import LineTracking
from motor import Motor
from servo import Servo
from ultrasonic import Ultrasonic
from rpi_ws281x import Color


class Tester:

    def __init__(self):
        self.buzzer = Buzzer()
        self.led = Led()
        self.motor = Motor()
        self.ultrasonic = Ultrasonic()
        self.line_tracking = LineTracking()
        self.servo = Servo()
        self.adc = ADC()

    def test_led(self):
        try:
            self.led.led_index(0x01, 255, 0, 0)  # Red
            self.led.led_index(0x02, 255, 125, 0)  # orange
            self.led.led_index(0x04, 255, 255, 0)  # yellow
            self.led.led_index(0x08, 0, 255, 0)  # green
            self.led.led_index(0x10, 0, 255, 255)  # cyan-blue
            self.led.led_index(0x20, 0, 0, 255)  # blue
            self.led.led_index(0x40, 128, 0, 128)  # purple
            self.led.led_index(0x80, 255, 255, 255)  # white'''
            print("The LED has been lit, the color is red orange yellow green cyan-blue blue white")
            time.sleep(3)  # wait 3s
            self.led.color_wipe(Color(0, 0, 0))  # turn off the light
            print("\nEnd of program")
        except KeyboardInterrupt:
            self.led.destroy()
            print("\nEnd of program")

    def test_motor(self):
        try:
            self.motor.set_speed(1000, 1000, 1000, 1000)  # Forward
            print("The car is moving forward")
            time.sleep(1)
            self.motor.set_speed(-1000, -1000, -1000, -1000)  # Back
            print("The car is going backwards")
            time.sleep(1)
            self.motor.set_speed(-1500, -1500, 2000, 2000)  # Left
            print("The car is turning left")
            time.sleep(1)
            self.motor.set_speed(2000, 2000, -1500, -1500)  # Right
            print("The car is turning right")
            time.sleep(1)
            self.motor.set_speed(0, 0, 0, 0)  # Stop
            print("\nEnd of program")
        except KeyboardInterrupt:
            self.motor.destroy()
            print("\nEnd of program")

    def test_ultrasonic(self):
        try:
            while True:
                data = self.ultrasonic.get_distance()  # Get the value
                print("Obstacle distance is " + str(data) + "CM")
                time.sleep(1)
        except KeyboardInterrupt:
            self.ultrasonic.destroy()
            print("\nEnd of program")

    def test_infrared(self):
        try:
            while True:
                if GPIO.input(self.line_tracking.IR01) is True and \
                        GPIO.input(self.line_tracking.IR02) is not True and \
                        GPIO.input(self.line_tracking.IR03) is not True:
                    print('Middle')
                elif GPIO.input(self.line_tracking.IR01) is not True \
                        and GPIO.input(self.line_tracking.IR02) is not True and \
                        GPIO.input(self.line_tracking.IR03) is True:
                    print('Right')
                elif GPIO.input(self.line_tracking.IR01) is True and \
                        GPIO.input(self.line_tracking.IR02) is not True \
                        and GPIO.input(self.line_tracking.IR03) is not True:
                    print('Left')
        except KeyboardInterrupt:
            self.line_tracking.destroy()
            print("\nEnd of program")

    def test_servo(self):
        try:
            while True:
                for i in range(50, 110, 1):
                    self.servo.set_servo_pwm('0', i)
                    time.sleep(0.01)
                for i in range(110, 50, -1):
                    self.servo.set_servo_pwm('0', i)
                    time.sleep(0.01)
                for i in range(80, 150, 1):
                    self.servo.set_servo_pwm('1', i)
                    time.sleep(0.01)
                for i in range(150, 80, -1):
                    self.servo.set_servo_pwm('1', i)
                    time.sleep(0.01)
        except KeyboardInterrupt:
            self.servo.set_servo_pwm('0', 90)
            self.servo.set_servo_pwm('1', 90)
            print("\nEnd of program")

    def test_adc(self):
        try:
            while True:
                left_idr = self.adc.recv(0)
                print("The photoresistor voltage on the left is " + str(left_idr) + "V")
                right_idr = self.adc.recv(1)
                print("The photoresistor voltage on the right is " + str(right_idr) + "V")
                power = self.adc.recv(2)
                print("The battery voltage is " + str(power * 3) + "V")
                time.sleep(1)
                print('\n')
        except KeyboardInterrupt:
            self.adc.destroy()
            print("\nEnd of program")

    def test_buzzer(self):
        try:
            self.buzzer.on()
            time.sleep(1)
            print("1S")
            time.sleep(1)
            print("2S")
            time.sleep(1)
            print("3S")
            self.buzzer.off()
            print("\nEnd of program")
        except KeyboardInterrupt:
            self.buzzer.off()
            print("\nEnd of program")


def main():
    print('Program is starting ... ')
    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        exit()
    tester = Tester()
    if sys.argv[1] == 'Led':
        tester.test_led()
    elif sys.argv[1] == 'Motor':
        tester.test_motor()
    elif sys.argv[1] == 'Ultrasonic':
        tester.test_ultrasonic()
    elif sys.argv[1] == 'Infrared':
        tester.test_infrared()
    elif sys.argv[1] == 'Servo':
        tester.test_servo()
    elif sys.argv[1] == 'ADC':
        tester.test_adc()
    elif sys.argv[1] == 'Buzzer':
        tester.test_buzzer()


# Main program logic follows:
if __name__ == '__main__':
    main()
