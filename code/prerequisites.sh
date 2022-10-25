#!/usr/bin/env sh
sudo apt update
sudo apt install -y i2c-tools python3-dev python3-pip python3-smbus python3-picamera
sudo pip install rpi_ws281x
