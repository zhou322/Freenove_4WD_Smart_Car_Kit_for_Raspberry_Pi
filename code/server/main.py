#!/usr/bin/python
# -*- coding: utf-8 -*-
import atexit
from threading import Thread

from thread_utils import *
from server import Server


class Runner:
    def __init__(self):
        self.start_tcp = False
        self.TCP_Server = Server()
        self.TCP_Server.connection_established = True
        self.stream_video = Thread(target=self.TCP_Server.stream_video)
        self.read_commands = Thread(target=self.TCP_Server.read_commands)
        self.power = Thread(target=self.TCP_Server.power)

    def shutdown(self):
        self.TCP_Server.connection_established = False
        try:
            stop_thread(self.read_commands)
            stop_thread(self.power)
            stop_thread(self.stream_video)
        except:
            pass
        self.TCP_Server.stop_tcp_server()

    def start(self):
        print("Open TCP")
        self.TCP_Server.start_tcp_server()
        self.read_commands.start()
        self.power.start()
        self.stream_video.start()


def main():
    runner = Runner()
    runner.start()
    atexit.register(runner.shutdown)


if __name__ == '__main__':
    main()
