#!/bin/bash -e
echo -e 'import machine\r\nmachine.reset()\r\n' > /dev/ttyUSB0
./serial.sh
