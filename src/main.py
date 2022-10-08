import gc
from hardware import Led
from config import config
from utils import print_traceback
from display import (
    turn_lights_off,
    display,
    display_ip,
    display_animation,
)
from constants import LOGO
import ujson as json
import ntptime
import urequests as requests
import time
from clock import get_time_text
import network


def connect_wifi():
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
                Led.on()
                routercon = network.WLAN(network.STA_IF)
                routercon.active(True)
                routercon.connect(ssid, password)
                ip_address = routercon.ifconfig()[0]
                if ip_address != '0.0.0.0':
                    Led.off()
            except Exception:
                time.sleep_ms(100)


def set_time():
    done = False
    while not done:
        try:
            ntptime.settime()
            done = True
        except Exception as error:
            print(error)
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

        response = getattr(requests, method
                           )(url, data=data, headers=headers).json()

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
        gc.collect()

        sources = load_sources()  # noqa: F841
        for _ in range(config['cycles_to_update']):
            for slide in config['slides']:
                millis = slide['millis'] if 'millis' in slide else 1000
                if slide['message'] == '{time}':
                    message = f'  {get_time_text()} '
                else:
                    message = slide['message']

                    if '{' in message:
                        source = slide['source']
                        message = message.replace(
                            '{', "sources['" + source + "']['"
                        )
                        message = message.replace('}', "']")
                        message = eval(message, {'sources': sources})

                # TODO conditional transition based on previous value

                if 'transitions' not in slide:
                    display(message, millis)
                    continue

                in_transition = slide['transitions'].get('in')
                if in_transition:
                    display_animation(
                        config['animations'][in_transition['animation']],
                        in_transition.get('cycles', 1)
                    )

                display(message, millis)

                out_transition = slide['transitions'].get('out')
                if out_transition:
                    display_animation(
                        config['animations'][out_transition['animation']],
                        out_transition.get('cycles', 1)
                    )


def start():
    first_call = True
    while True:
        turn_lights_off()
        Led.off()

        # connect_wifi()
        if first_call:
            display(LOGO, 2000)
            display_animation(config['animations']['loading_1'], 3)
            if config['display_ip']:
                display_ip()
            set_time()

        try:
            loop()
            first_call = False
        except Exception as error:
            print_traceback(error)


start()
