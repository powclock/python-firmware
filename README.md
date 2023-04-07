# Firmware
Powclock's firmware

## Hardware

This device uses a ESP8266. When connected via USB to a computer, it can be programmed via Serial port. The ID of the device is:
`ID 1a86:7523 QinHeng Electronics CH340 serial converter`

To interact with the device from a computer with ArchLinux, the following setup commands can be used:
```
yay -S esptool-git
pacman -S python-dotenv
pip install adafruit-ampy
```

## MicroPython

Original firmware of micropython can be downloaded from the official website: https://micropython.org/download/esp8266/
The current project is expected to run with 1.19.1, but older releases may also work
Documentation about the firmware version can be found also at the official website: https://docs.micropython.org/en/v1.19.1/
To build the firmware for this platform, this instructions can be used:
```
git clone --recursive https://github.com/nicovell3/esp-open-sdk
cd esp-open-sdk
docker build -t esp-open-sdk .

cd ../
git clone https://github.com/micropython/micropython
docker run --rm -v $PWD:$PWD -u $UID -w $PWD esp-open-sdk make -C ports/esp8266 submodules
docker run --rm -v $PWD:$PWD -u $UID -w $PWD esp-open-sdk make -C mpy-cross
docker run --rm -v $PWD:$PWD -u $UID -w $PWD esp-open-sdk make -C ports/esp8266 -j BOARD=GENERIC

cd ..
chown -R $USER:$USER esp-open-sdk micropython
mv micropython/ports/esp8266/build-GENERIC/firmware-combined.bin esp8266-master.bin
```

## Files

### Scripts
Inside the scripts folder, the following files can be found:
- env.sh - Meant to configure the tty device to interact with
- flash.sh - Change the entire MicroPython firmware. The bin filename can be passed as an argument.
- put.sh - Add only one Python file from the src folder (passed as argument without path), reboot and connect to serial. Example: `./put.sh main.py`
- reset.sh - Reboot the device and connect to serial
- serial.sh - Connect to the serial device
- upload.sh - Add all Python files in the src folder

### Src
These are the files meant to be executed by PowClock:
- boot.py - Initial file to interact directly with the board
- config.py - Default configuration and handler
- config.json - Initial custom configuration file (meant to be changed at start time)
- display.py - 7-segments display manager
- httpServer.py - Server only meant for the initial configuration
- index.html - HTML file to be served by the HTTP server at config time
- main.py - Main functions to be run during the PowClock operation
- powRequests.py - Latest urequests file a little customized for this project. This function uses to produce an unrecoverable error which resets the board automatically. The alternative is to use the default function from urequests, which hangs the board forever until a manual reboot is made.

# Initial configuration

To start with PowClock, just plug it in, wait until the messages "setup" and "192.168.4.1" appear and connect to the WiFi hotspot called "Powclock" with password "asdfasdf".

You can then open a web browser to configure your WiFi net from the following link: http://192.168.4.1

You can also directly send your JSON data through curl with the following command:

```
cat << EOF | curl -X POST --data @- http://192.168.4.1/config.json
{
  "wificlient": {
    "ssid": "My WiFi net",
    "password": "My secure password"
  }
}
EOF
```

## Aditional configurations

You can refer to config.py to see which additional configurations can be changed. No config validation is performed, so take care while modifying them. These additional configs can be useful:

- setup - change the setup configuration SSID and password. It is recommended to change it to avoid someone from taking control of your PowClock when it can't connect to your WiFi network.
- night_mode - an array of two hours must be provided to use the display with low brightness. An empty array will force low brightness mode forever.
- utc_offset - default UTC offset in seconds.
- utc_offset_update - boolean to select if PowClock should correct the UTC offset.
- timezone - can be empty to use the IP to select it or chosen between the ones in http://worldtimeapi.org/timezones
- cycles_to_update - decide when are HTTP requests made during normal operation.
- cycles_to_reboot - shouldn't be necessary, but allows to perform a silent reboot during normal operation.
- sources - contains which webs (which return a JSON object) should be called during the loop. 
- slides - configures the slides format and duration.

## Tips and tricks

To enter setup mode, just force a boot error. You can do that by resetting the PowClock in the reset button (which is placed at the ESP8266 board, next to the USB) and reset it again when the logo appears.

If you want to add your own source, try to avoid too long responses. The RAM memory is limited and it my break while trying to download the response or parsing the JSON structure.

If you are attached to the serial screen, you can leave it with "Ctrl+A" "k". This will kill the screen.

When trying modifications, the log can be saved to a file running the following command:
```
screen -L -S powclock /dev/ttyUSB0 115200
```
If after that command you want to leave the screen running, just type "Ctrl+A" "d" to detach. Then, use `screen -rd` to reattach or inspect the screenlog.0 file.

When attached to the serial output, you can type "Ctrl+C" to use interactive mode. The main loop will stop.