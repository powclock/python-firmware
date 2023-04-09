config = {
    "update": {
        "enabled": True,
        "url": "https://raw.githubusercontent.com",
        "repo": "powclock/firmware-python",
        "branch": "master",
        "descriptor": "update.json",
    },
    "wificlient": {
        "ssid": "",
        "password": ""
    },
    "setup": {
        "ssid": "Powclock",
        "password": "asdfasdf"
    },
    "night_mode": ['20:00', '8:00'],
    "utc_offset": 3600, #specified in seconds
    "utc_offset_update": True,
    "timezone": "",
    "cycles_to_update": 3,
    "cycles_to_reboot": 0,
    "sources": {
        "powclock_api": {
            "url": "http://api.powclock.com/v1",
            "method": "get",
            "attributes": {
                "price": ["price","usd"], #This will get data like .price.usd
                "height": ["height"]
            }
        }
    },
    "slides": [
        {
            "message": "{time}",
            "millis": 6000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            },
        },
        {
            "message": "{date}",
            "millis": 3000,
        },
        {
            "message": "usd",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        },
        {
            "source": "powclock_api",
            "message": "{price}",
            "millis": 6000
        },
        {
            "message": "sats",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        },
        {
            "source": "powclock_api",
            "message": "int(1e8/{price})",
            "animations": {
                "up": "loading_1",
                "down": "trending_down_1"
            },
            "millis": 6000
        },
        {
            "message": "height",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        },
        {
            "source": "powclock_api",
            "message": "{height}",
            "millis": 6000
        }
    ],
    "animations": {
        "trending_up_1": {
            "messages": ["     ⬇  ", "      - ", "       ⬆"],
            "millis": 100
        },
        "trending_down_1": {
            "messages": ["     ⬆  ", "      - ", "       ⬇"],
            "millis": 100
        },
        "loading_1": {
            "messages": [
                "↙       ", "↖       ", "⬆       ", " ⬆      ", "  ⬆     ",
                "   ⬆    ", "    ⬆   ", "     ⬆  ", "      ⬆ ", "       ⬆",
                "       ↗", "       ↘", "       ⬇", "      ⬇ ", "     ⬇  ",
                "    ⬇   ", "   ⬇    ", "  ⬇     ", " ⬇      ", "⬇       "
            ],
            "millis": 5
        },
        "loading_2": {
            "messages": [
                "↙       ", "↖       ", "⬆       ", " ⬆      ", "  ⬆     ",
                "   ⬆    ", "   ↗    ", "    ↙   ", "    ⬇   ", "     ⬇  ",
                "      ⬇ ", "       ⬇", "       ↘", "       ↗", "       ⬆",
                "      ⬆ ", "     ⬆  ", "    ⬆   ", "    ↖   ", "   ↘    ",
                "   ⬇    ", "  ⬇     ", " ⬇      ", "⬇       "
            ],
            "millis": 5
        },
        "blink_1": {
            "messages": [" ------ ", ""],
            "millis": 500
        }
    }
}

def loadConfig():
    import ujson
    try:
        with open('./config.json', 'r') as input_file:
            config.update(ujson.load(input_file))
    except Exception as error:
        print('Error loading JSON from ./config.json')

