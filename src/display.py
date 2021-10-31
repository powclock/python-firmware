from constants import (
    SYMBOLS,
    DISPLAY_DIGITS,
    REFRESH_DELAY
)
import micropython
from hardware import (
    data as t,
    clock as c,
    latch as h
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
    h.off()
    for _ in range(16):
        c.off()
        t.on()
        c.on()
    h.on()


def lights_off(method):
    def _lights_off(*args, **kwargs):
        turn_lights_off()
        result = method(*args, **kwargs)
        turn_lights_off()
        return result
    return _lights_off


@micropython.native
def display_cycle(e, b, n, r, d):
    for i in range(len(b)):
        p = n[:]
        h.off()

        for j in r:
            if j < 8 and j != i:
                p[j] = 1
                c.off()
                t.value(p[j] ^ 1)
                c.on()
                continue

            if j > 7 and b[i][j - 8]:
                c.off()
                t.value(p[j])
                c.on()
                continue

            c.off()
            t.value(p[j] ^ 1)
            c.on()

        h.on()

        if d:
            h.off()
            for _ in r:
                c.off()
                t.on()
                c.on()
            h.on()

        time.sleep_us(e)

    h.off()
    for _ in r:
        c.off()
        t.on()
        c.on()
    h.on()


@lights_off
def display(
    message,
    millis=1000,
    dark=None,
    mid_flash=False,
    initial_flash=False
):
    if isinstance(message, list):
        bit_lines = message
    else:
        message = str(message)[:DISPLAY_DIGITS]
        left_zeros = DISPLAY_DIGITS - len(message)
        padded_message = left_zeros * [' '] + [symbol for symbol in message]
        bit_lines = [SYMBOLS[item] for item in padded_message]

    half_digits = int(DISPLAY_DIGITS / 2)
    bit_lines = bit_lines[half_digits:] + bit_lines[:half_digits]
    line = array('b', 16 * [0])
    reversed_indexes = array('b', reversed(range(16)))

    if dark is None:
        dark = STATE['dark_mode']

    b = bit_lines
    n = line
    y = display_cycle
    r = reversed_indexes
    m = millis
    d = dark
    e = REFRESH_DELAY

    if millis < 1000 or (not mid_flash and not initial_flash):
        s = time.ticks_ms()
        while (time.ticks_ms() - s < m):
            y(e, b, n, r, d)
    else:
        flash_millis = 200
        f = flash_millis
        if initial_flash:
            s = time.ticks_ms()
            while (time.ticks_ms() - s < f):
                y(e, b, n, r, True)

            s = time.ticks_ms()
            while (time.ticks_ms() - s < f):
                y(e, b, n, r, False)

            s = time.ticks_ms()
            g = m - 2 * f
            while (time.ticks_ms() - s < g):
                y(e, b, n, r, True)


@lights_off
def display_ip(dark=None):
    routercon = network.WLAN(network.STA_IF)
    ip_address = routercon.ifconfig()[0]
    splits = ip_address.split('.')
    display('addr', 2000, dark=dark)
    display(' '.join(splits[:2]), 2000, dark=dark)
    display(' '.join(splits[2:]), 2000, dark=dark)


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

    display(hour + '_' + minutes, millis)
