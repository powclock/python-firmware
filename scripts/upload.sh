#!/bin/bash
cd $(dirname $0)
source env.sh
find ../src/*{.py,.json} -exec echo {} \;  -exec ampy --port $TTY put {} \;
./serial.sh
