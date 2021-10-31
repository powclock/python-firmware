from constants import LOGO
from display import (
    turn_lights_off,
    display,
    display_time,
    display_ip
)
from utils import print_trace
from config import config
from hardware import Led
import network
import time
import urequests as requests
import ntptime
import ujson as json
import gc


def connect_wifi():
    ssid = config['wireless']['ssid']
    password = config['wireless']['password']

    connected = False
    while not connected:
        try:
            Led.on()
            routercon = network.WLAN(network.STA_IF)
            routercon.active(True)
            routercon.connect(ssid, password)
            ip_address = routercon.ifconfig()[0]
            if ip_address != '0.0.0.0':
                connected = True
                Led.off()
        except Exception:
            time.sleep_ms(500)


def set_time():
    done = False
    while not done:
        try:
            ntptime.settime()
            done = True
        except Exception:
            time.sleep_ms(500)


def display_animation(animation, cycles=1, message_mask=None, dark=None):
    for _ in range(cycles):
        for i, message in enumerate(animation['messages']):
            if message_mask:
                new_message = ''
                for j, symbol in enumerate(message_mask):
                    if symbol != ' ':
                        new_message += symbol
                    else:
                        new_message += message[j]
                message = new_message

            if isinstance(animation['millis'], list):
                millis = animation['millis'][i]
            else:
                millis = animation['millis']

            display(message, millis, dark=dark)


def load_sources():
    display_animation(config['animations']['loading_2'], 2)

    sources = {}
    for source, source_config in config['sources'].items():
        url = source_config['url']
        method = source_config['method'].lower()

        data = None
        if 'data' in source_config:
            data = json.dumps(source_config['data'])

        headers = {}
        if 'headers' in source_config:
            headers = source_config['headers']

        response = getattr(requests, method)(
            url,
            data=data,
            headers=headers
        ).json()

        sources[source] = {}
        for attribute, path in config['sources'][source]['attributes'].items():
            value = response
            for item in path:
                value = value[item]
            sources[source][attribute] = value

    display_animation(config['animations']['loading_2'], 2)
    return sources


def loop():
    while True:
        sources = load_sources()  # noqa: F841
        for _ in range(config['cycles_to_update']):
            for slide in config['slides']:
                millis = slide['millis'] if 'millis' in slide else 1000
                if slide['message'] == '{time}':
                    display_time(2000, millis)
                else:
                    message = slide['message']

                    if '{' in message:
                        source = slide['source']
                        message = message.replace(
                            '{', "sources['" + source + "']['")
                        message = message.replace('}', "']")
                        message = eval(message, {'sources': sources})

                    display(message, millis)


def main(first_call=True):
    turn_lights_off()
    Led.off()

    gc.collect()

    if first_call:
        display_animation(config['animations']['loading_1'])
        display(LOGO, 500, dark=True)
        display(LOGO, 150)
        display(LOGO, 500, dark=True)

    connect_wifi()
    if first_call:
        if config['display_ip']:
            display_ip()
        set_time()

    try:
        loop()
    except Exception as error:
        print_trace(error)
        main(first_call=False)


if __name__ == "__main__":
    main()
