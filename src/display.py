from constants import DISPLAY_DIGITS, SYMBOLS
import micropython
from hardware import data, clock, latch
from array import array
import time
from config import config
import network


STATE = {
    'dark_mode': False
}


@micropython.native
def turn_lights_off():
    latch.off()
    for _ in range(16):
        clock.off()
        data.on()
        clock.on()
    latch.on()


def lights_off(method):
    def _lights_off(*args, **kwargs):
        turn_lights_off()
        result = method(*args, **kwargs)
        turn_lights_off()
        return result
    return _lights_off


@micropython.native
def _display_cycle(bit_lines, line, reversed_indexes, dark):
    refresh_delay = config['refresh_delay']
    for i, bit_line in enumerate(bit_lines):
        line_copy = line[:]
        latch.off()

        for j in reversed_indexes:
            if j < 8 and j != i:
                line_copy[j] = 1
                clock.off()
                data.value(line_copy[j] ^ 1)
                clock.on()
                continue

            if j > 7 and bit_line[j - 8]:
                clock.off()
                data.value(line_copy[j])
                clock.on()
                continue

            clock.off()
            data.value(line_copy[j] ^ 1)
            clock.on()

        latch.on()

        if dark:
            latch.off()
            for _ in reversed_indexes:
                clock.off()
                data.on()
                clock.on()
            latch.on()

        time.sleep_us(refresh_delay)


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

    if millis < 1000 or (not mid_flash and not initial_flash):
        start_millis = time.ticks_ms()
        while (time.ticks_ms() - start_millis < millis):
            _display_cycle(bit_lines,
                           line,
                           reversed_indexes,
                           dark)
    else:
        flash_millis = 200
        if initial_flash:
            start_millis = time.ticks_ms()
            while (time.ticks_ms() - start_millis < flash_millis):
                _display_cycle(bit_lines,
                               line,
                               reversed_indexes,
                               dark=True)

            phase_start_millis = time.ticks_ms()
            while (time.ticks_ms() - phase_start_millis < flash_millis):
                _display_cycle(bit_lines,
                               line,
                               reversed_indexes,
                               dark=False)

            start_millis = time.ticks_ms()
            remaining_millis = millis - 2 * flash_millis
            while (time.ticks_ms() - start_millis < remaining_millis):
                _display_cycle(bit_lines,
                               line,
                               reversed_indexes,
                               dark=True)


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
