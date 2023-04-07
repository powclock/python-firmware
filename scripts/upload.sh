#!/bin/bash -e
cd $(dirname $0)
source ./env.sh
find ../src/*{.py,.json,.html} -exec echo {} \;  -exec ampy --port $TTY put {} \;
echo -e 'import machine\r\nmachine.reset()\r\n' > /dev/ttyUSB0
./serial.sh
