# -*-coding: utf-8 -*-
import time
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT = 8  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53


# Define functions which animate LEDs in various ways.
class Led:
    def __init__(self):
        # Control the sending order of color data
        self.mode = None
        self.ORDER = "RGB"
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                                       LED_CHANNEL)
        # Initialize the library (must be called once before other functions).
        self.strip.begin()

    def led_type(self, order, r_g_b):
        B = r_g_b & 255
        G = r_g_b >> 8 & 255
        R = r_g_b >> 16 & 255
        LED_TYPES = {"GRB": Color(G, R, B),
                     "GBR": Color(G, B, R),
                     "RGB": Color(R, G, B),
                     "RBG": Color(R, B, G),
                     "BRG": Color(B, R, G),
                     "BGR": Color(B, G, R)}
        if order in LED_TYPES:
            return LED_TYPES[order]

    def color_wipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color = self.led_type(self.ORDER, color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()
        time.sleep(wait_ms / 1000.0)

    def theater_chase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        color = self.led_type(self.ORDER, color)
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        return self.led_type(self.ORDER, Color(r, g, b))

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def rainbow_cycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def led_index(self, index, red, green, blue):
        color = self.led_type(self.ORDER, Color(red, green, blue))
        for i in range(8):
            if index & 0x01 == 1:
                self.strip.setPixelColor(i, color)
                self.strip.show()
            index = index >> 1

    def led_mode(self, n):
        self.mode = n
        while True:
            if self.mode == '1':
                self.color_wipe(Color(255, 0, 0))  # Red wipe
                self.color_wipe(Color(0, 255, 0))  # Green wipe
                self.color_wipe(Color(0, 0, 255))  # Blue wipe
                self.color_wipe(Color(0, 0, 0), 10)
            elif self.mode == '2':
                self.theater_chase_rainbow()
                self.color_wipe(Color(0, 0, 0), 10)
            elif self.mode == '3':
                self.rainbow()
                self.color_wipe(Color(0, 0, 0), 10)
            elif self.mode == '4':
                self.rainbow_cycle()
                self.color_wipe(Color(0, 0, 0), 10)
            else:
                self.color_wipe(Color(0, 0, 0), 10)
                break

    def destroy(self):
        self.color_wipe(Color(0, 0, 0), 10)


def main():
    print('Program is starting ... ')
    led = Led()
    try:
        while True:
            print("Chaser animation")
            led.color_wipe(Color(255, 0, 0))  # Red wipe
            led.color_wipe(Color(0, 255, 0))  # Green wipe
            led.color_wipe(Color(0, 0, 255))  # Blue wipe
            led.theater_chase_rainbow()
            print("Rainbow animation")
            led.rainbow()
            led.rainbow_cycle()
            led.color_wipe(Color(0, 0, 0), 10)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        led.destroy()


# Main program logic follows:
if __name__ == '__main__':
    main()
