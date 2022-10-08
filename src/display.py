from constants import (
    DISPLAY_DIGITS,
    REFRESH_DELAY,
    ALL_SYMBOLS,
)
import micropython
from hardware import (
    clock,
    data,
    latch,
)
from array import array
from config import config
import network
import time

STATE = {'night_mode': False}


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
def _display(bit_lines, millis, night_mode=False):
    reversed_indexes = array('b', reversed(range(16)))

    screen_lines = []
    for bit_line_index, bit_line in enumerate(bit_lines):
        values = []
        for reversed_index in reversed_indexes:
            value = 0
            if reversed_index < 8 and reversed_index != bit_line_index:
                value = 1
                values.append(0)
                continue
            elif reversed_index > 7 and bit_line[reversed_index - 8]:
                values.append(value)
                continue
            values.append(value ^ 1)

        screen_lines.append(values)

    start_time = time.ticks_ms()
    while (time.ticks_ms() - start_time < millis):
        for screen_line in screen_lines:
            latch.off()
            for bit in screen_line:
                clock.off()
                data.value(bit)
                clock.on()
            latch.on()

            if night_mode:
                latch.off()
                for _ in range(16):
                    clock.off()
                    data.on()
                    clock.on()
                latch.on()
            time.sleep_us(REFRESH_DELAY)


@lights_off
def display(
    message,
    millis=None,
    night_mode=None,
):
    if millis is None:
        millis = 1000

    if night_mode is None:
        night_mode = STATE['night_mode']

    if 'night_mode' in config:
        current_time = time.gmtime(time.time())
        hour = str((current_time[3] + config['utc_offset']) % 24)
        minutes = str(current_time[4])

        if config['night_mode'] is True:
            STATE['night_mode'] = True

        elif config['night_mode'] is False:
            STATE['night_mode'] = False

        else:
            start_hour, start_minutes = config['night_mode'][0].split(':')
            stop_hour, stop_minutes = config['night_mode'][1].split(':')
            if ((int(hour) >= int(start_hour) or int(hour) <= int(stop_hour))
                    and (int(minutes) >= int(start_minutes)
                         or int(minutes) <= int(stop_minutes))):
                STATE['night_mode'] = True
            else:
                STATE['night_mode'] = False

    if isinstance(message, list):
        bit_lines = message
    else:
        message = str(message)
        left_zeros = DISPLAY_DIGITS - len(message)
        padded_message = left_zeros * [' '] + [symbol for symbol in message]
        bit_lines = [ALL_SYMBOLS[item] for item in padded_message]

    bit_lines = bit_lines[4:] + bit_lines[:4]
    _display(bit_lines, millis, night_mode)


def display_ip(night_mode=None):
    routercon = network.WLAN(network.STA_IF)
    ip_address = routercon.ifconfig()[0]
    splits = ip_address.split('.')
    display('addr', 2000, night_mode=night_mode)
    display(' '.join(splits[:2]), 2000, night_mode=night_mode)
    display(' '.join(splits[2:]), 2000, night_mode=night_mode)


def display_animation(
    animation,
    cycles=None,
    night_mode=None,
):
    if cycles is None:
        cycles = 1

    for _ in range(cycles):
        for i, message in enumerate(animation['messages']):
            if isinstance(animation['millis'], list):
                millis = animation['millis'][i]
            else:
                millis = animation['millis']
            display(
                message,
                millis,
                night_mode=night_mode,
            )
