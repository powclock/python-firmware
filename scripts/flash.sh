#!/bin/bash
esptool.py --port /dev/cu.usbserial-210 erase_flash
esptool.py --port /dev/cu.usbserial-210 --baud 460800 write_flash --flash_size=detect 0 esp8266-*.bin
