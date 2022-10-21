import time
import RPi.GPIO as GPIO


class Buzzer:
    def __init__(self):
        self.buzzer_pin = 17
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)

    def run(self, command):
        if command != '0':
            self.on()
        else:
            self.off()

    def on(self):
        GPIO.output(self.buzzer_pin, True)

    def off(self):
        GPIO.output(self.buzzer_pin, False)


def main():
    buzzer = Buzzer()
    buzzer.on()
    time.sleep(3)
    buzzer.off()


if __name__ == '__main__':
    main()
