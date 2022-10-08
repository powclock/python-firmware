#!/bin/bash
cd $(dirname $0)
source env.sh
ampy --port $TTY put ../src/$1
./serial.sh
