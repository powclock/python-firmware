#!/bin/bash -e
cd $(dirname $0)
source ./env.sh
ampy --port $TTY put ../src/$1
echo -e 'import machine\r\nmachine.reset()\r\n' > /dev/ttyUSB0
./serial.sh
