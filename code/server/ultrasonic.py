from motor import *
import RPi.GPIO as GPIO
from servo import *


class Ultrasonic:
    def __init__(self):
        GPIO.setwarnings(False)
        self.trigger_pin = 27
        self.echo_pin = 22
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        self.motor = Motor()
        self.servo = Servo()

    def send_trigger_pulse(self):
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00015)
        GPIO.output(self.trigger_pin, False)

    def wait_for_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.echo_pin) != value and count > 0:
            count = count - 1

    def get_distance(self):
        distance_cm = [0, 0, 0, 0, 0]
        for i in range(3):
            self.send_trigger_pulse()
            self.wait_for_echo(True, 10000)
            start = time.time()
            self.wait_for_echo(False, 10000)
            finish = time.time()
            pulse_len = finish - start
            distance_cm[i] = pulse_len / 0.000058
        distance_cm = sorted(distance_cm)
        return int(distance_cm[2])

    def run_motor(self, left, middle, right):
        if (left < 30 and middle < 30 and right < 30) or middle < 30:
            self.motor.set_speed(-1450, -1450, -1450, -1450)
            time.sleep(0.1)
            if left < right:
                self.motor.set_speed(1450, 1450, -1450, -1450)
            else:
                self.motor.set_speed(-1450, -1450, 1450, 1450)
        elif left < 30 and middle < 30:
            self.motor.set_speed(1500, 1500, -1500, -1500)
        elif right < 30 and middle < 30:
            self.motor.set_speed(-1500, -1500, 1500, 1500)
        elif left < 20:
            self.motor.set_speed(2000, 2000, -500, -500)
            if left < 10:
                self.motor.set_speed(1500, 1500, -1000, -1000)
        elif right < 20:
            self.motor.set_speed(-500, -500, 2000, 2000)
            if right < 10:
                self.motor.set_speed(-1500, -1500, 1500, 1500)
        else:
            self.motor.set_speed(600, 600, 600, 600)

    def run(self):
        for i in range(30, 151, 60):
            self.servo.set_servo_pwm('0', i)
            time.sleep(0.2)
            if i == 30:
                left = self.get_distance()
            elif i == 90:
                middle = self.get_distance()
            else:
                right = self.get_distance()
        while True:
            for i in range(90, 30, -60):
                self.servo.set_servo_pwm('0', i)
                time.sleep(0.2)
                if i == 30:
                    left = self.get_distance()
                elif i == 90:
                    middle = self.get_distance()
                else:
                    right = self.get_distance()
                self.run_motor(left, middle, right)
            for i in range(30, 151, 60):
                self.servo.set_servo_pwm('0', i)
                time.sleep(0.2)
                if i == 30:
                    left = self.get_distance()
                elif i == 90:
                    middle = self.get_distance()
                else:
                    right = self.get_distance()
                self.run_motor(left, middle, right)

    def destroy(self):
        self.servo.set_servo_pwm('0', 90)
        self.motor.set_speed(0, 0, 0, 0)


def main():
    print('Program is starting ... ')
    ultrasonic = Ultrasonic()
    try:
        ultrasonic.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        ultrasonic.destroy()


# Main program logic follows:
if __name__ == '__main__':
    main()
