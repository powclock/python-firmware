from constants import (
    DISPLAY_DIGITS,
    REFRESH_DELAY,
    DARK_REFRESH_DELAY,
    NUMBERS_SYMBOLS,
    LETTERS_SYMBOLS,
    ANIMATION_SYMBOLS
)
import micropython
from hardware import (
    clock as c,
    data as d,
    latch as t
)
from array import array
import time
from config import config
import network


STATE = {
    'dark_mode': False
}


@micropython.native
def turn_lights_off():
    t.off()
    for _ in range(16):
        c.off()
        d.on()
        c.on()
    t.on()


def lights_off(method):
    def _lights_off(*args, **kwargs):
        turn_lights_off()
        result = method(*args, **kwargs)
        turn_lights_off()
        return result
    return _lights_off


@micropython.native
def _display(
    bit_lines,
    millis,
    dark_mode
):
    line = array('b', 16 * [0])
    reversed_indexes = array('b', reversed(range(16)))

    k = dark_mode
    p = bit_lines
    n = line
    r = reversed_indexes
    m = millis
    u = REFRESH_DELAY
    z = DARK_REFRESH_DELAY

    x = time.ticks_ms
    w = x()
    while (x() - w < m):
        for i, s in enumerate(p):
            b = n[:]
            t.off()
            for j in r:
                if j < 8 and j != i:
                    b[j] = 1
                    c.off()
                    d.value(b[j] ^ 1)
                    c.on()
                    continue
                if j > 7 and s[j - 8]:
                    c.off()
                    d.value(b[j])
                    c.on()
                    continue
                c.off()
                d.value(b[j] ^ 1)
                c.on()
            t.on()
            if not k:
                time.sleep_us(u)
            else:
                t.off()
                for _ in range(16):
                    c.off()
                    d.on()
                    c.on()
                t.on()
                time.sleep_us(z)


@lights_off
def display(
    message,
    millis=1000,
    symbols=None,
    dark_mode=None
):
    if dark_mode is None:
        dark_mode = STATE['dark_mode']

    if isinstance(message, list):
        bit_lines = message
    else:
        if symbols is None:
            try:
                int(message)
                symbols = NUMBERS_SYMBOLS
            except Exception:
                symbols = LETTERS_SYMBOLS

        message = str(message)
        left_zeros = DISPLAY_DIGITS - len(message)
        padded_message = left_zeros * [' '] + [symbol for symbol in message]
        bit_lines = [symbols[item] for item in padded_message]

    bit_lines = bit_lines[4:] + bit_lines[:4]
    _display(bit_lines, millis, dark_mode)


@lights_off
def display_ip(dark=None):
    routercon = network.WLAN(network.STA_IF)
    ip_address = routercon.ifconfig()[0]
    splits = ip_address.split('.')
    display('addr', 2000, LETTERS_SYMBOLS)
    display(' '.join(splits[:2]), 2000, NUMBERS_SYMBOLS)
    display(' '.join(splits[2:]), 2000, NUMBERS_SYMBOLS)


@lights_off
def display_time(millis, dark=None):
    current_time = time.gmtime(time.time())

    hour = str((current_time[3] + config['utc_offset']) % 24)
    if len(hour) == 1:
        hour = '0' + hour

    minutes = str(current_time[4])
    if len(minutes) == 1:
        minutes = '0' + minutes

    if 'dark_mode' in config:
        if config['dark_mode'] is True:
            STATE['dark_mode'] = True
        elif config['dark_mode'] is False:
            STATE['dark_mode'] = False
        else:
            start_hour, start_minutes = config['dark_mode'][0].split(':')
            stop_hour, stop_minutes = config['dark_mode'][1].split(':')
            if ((int(hour) >= int(start_hour) or int(hour) <= int(stop_hour))
                and (int(minutes) >= int(start_minutes)
                     or int(minutes) <= int(stop_minutes))):
                STATE['dark_mode'] = True
            else:
                STATE['dark_mode'] = False

    display(hour + '_' + minutes, millis, NUMBERS_SYMBOLS)


def display_animation(animation, cycles=1):
    for _ in range(cycles):
        for i, message in enumerate(animation['messages']):
            if isinstance(animation['millis'], list):
                millis = animation['millis'][i]
            else:
                millis = animation['millis']
            display(message, millis, ANIMATION_SYMBOLS)
