import time
import os
from threading import Thread
from command import COMMAND, COMMAND_SEPARATOR, COMMAND_TERMINATOR
from thread_utils import *
from control import Control

class CustomClient:
    def __init__(self):
        self.led_index = None
        self.streaming_thread = None
        self.receive_thread = None
        self.target_host = 'raspberrypi-00.local'
        self.control = None
        self.servo1 = 90
        self.servo2 = 90
        self.connected = False

    def connect(self):
        try:
            self.control = Control(self.target_host)
            self.receive_thread = Thread(target=self.recv_message)
            self.receive_thread.start()
        except Exception as e:
            print(e)
            print('control error')
            return

        print('Server address:' + str(self.target_host) + '\n')
        self.connected = True

    def go_straight(self, timeout_in_seconds):
        start = time.time()
        while time.time() < start + timeout_in_seconds:
            forward = COMMAND_SEPARATOR + str(4095) + COMMAND_SEPARATOR + str(4095) + COMMAND_SEPARATOR + str(
                4095) + COMMAND_SEPARATOR + str(4095) + COMMAND_TERMINATOR
            self.control.send_data(COMMAND.CMD_MOTOR + forward)
            time.sleep(0.5)
            forward = COMMAND_SEPARATOR + str(0) + COMMAND_SEPARATOR + str(0) + COMMAND_SEPARATOR + str(
                0) + COMMAND_SEPARATOR + str(0) + COMMAND_TERMINATOR
            self.control.send_data(COMMAND.CMD_MOTOR + forward)

if __name__ == '__main__':
    custom_client = CustomClient()
    custom_client.connect()
    custom_client.go_straight(1)