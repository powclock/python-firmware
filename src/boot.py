from update import update_firmware
from machine import freq
import gc
from config import config
from utils import print_traceback
from hardware import Led
from display import turn_lights_off
from os import listdir, rename


turn_lights_off()
Led.off()
freq(int(16e7))  # 160 MHz
gc.enable()

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
