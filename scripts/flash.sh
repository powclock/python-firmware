#!/bin/bash -e
source ./env.sh
echo "Erasing flash"
esptool.py --port $TTY erase_flash
if [ "$1" = "" ]; then
	firmware="esp8266-20220618-v1.19.1.bin"
else
	firmware="$1"
fi
echo "Uploading flash"
esptool.py --port $TTY --baud 460800 write_flash --flash_size=detect 0 "$firmware"
