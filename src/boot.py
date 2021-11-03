from update import update_firmware
from machine import freq
import gc
from config import config
from utils import print_traceback


freq(int(16e7))  # 160 MHz
gc.enable()

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
