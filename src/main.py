from hardware import Led
from config import config
from utils import print_traceback
from display import (
    turn_lights_off,
    display,
    display_time,
    display_ip,
    display_animation
)
from constants import LOGO
import ujson as json
import ntptime
import urequests as requests
import time
import network
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
    gc.collect()
    turn_lights_off()
    Led.off()

    if first_call:
        display(LOGO, 2000)
        display_animation(config['animations']['loading_1'], 3)

    connect_wifi()
    if first_call:
        if config['display_ip']:
            display_ip()
        set_time()

    try:
        loop()
    except Exception as error:
        print_traceback(error)
        main(first_call=False)


if __name__ == "__main__":
    main()
