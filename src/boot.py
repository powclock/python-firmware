from update import update_firmware
from machine import freq
import gc
from config import config
from utils import print_traceback
from hardware import Led
from display import turn_lights_off
from os import listdir, rename
import utime as time

turn_lights_off()
Led.off()
# freq(int(8e7))  # 80 MHz
freq(int(16e7))  # 160 MHz
gc.enable()


def connect():
    import network
    try:
        with open('wifi.dat') as myfile:
            lines = myfile.readlines()
    except OSError:
        lines = []

    profiles = {}
    for line in lines:
        ssid, password = line.strip().split(';')
        profiles[ssid] = password

    for ssid, password in profiles.items():
        print(f'Connecting to {ssid}...')
        for _ in range(100):
            try:
                print('.', end='')
                routercon = network.WLAN(network.STA_IF)
                routercon.active(True)
                routercon.connect(ssid, password)
                ip_address = routercon.ifconfig()[0]
                if ip_address != '0.0.0.0':
                    return True
            except Exception as error:
                print(error)
            finally:
                time.sleep_ms(100)

    return False


def connect_wifi():
    if connect():
        gc.collect()
        return

    def _connect():
        from wifi_manager import WifiManager
        wm = WifiManager()
        wm.connect()

    _connect()


connect_wifi()
gc.collect()

for file_name in listdir():
    if file_name[0] == ('_'):
        rename(file_name, file_name[1:])

do_update = 'update' in config \
    and 'enabled' in config['update'] \
    and config['update']['enabled']
if do_update:
    try:
        print('Updating firmware...')
        update_firmware()
        print('Firmware updated!')
    except Exception as error:
        print('Failed to update firmware!')
        print_traceback(error)
