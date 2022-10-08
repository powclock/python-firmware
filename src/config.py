import ujson as json
from utils import print_traceback

config = {
    "update": {
        "enabled": True,
        "url": "https://raw.githubusercontent.com",
        "repo": "powclock/firmware-python",
        "branch": "master",
        "descriptor": "update.json",
    },
    # "night_mode": ['23:00', '7:00'],
    "night_mode": False,
    "utc_offset": 2,
    "display_ip": True,
    "cycles_to_update": 3,
    "sources": {
        "powclock_api": {
            "url": "https://api.powclock.com/v1",
            "method": "get",
            "attributes": {
                "price": ["price", "usd"],
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
        }, {
            "message": "usd",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        }, {
            "source": "powclock_api",
            "message": "{price}",
            "millis": 6000
        }, {
            "message": "sats",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        }, {
            "source": "powclock_api",
            "message": "int(1e8/{price})",
            "animations": {
                "up": "loading_1",
                "down": "trending_down_1"
            },
            "millis": 6000
        }, {
            "message": "height",
            "millis": 2000,
            "transitions": {
                "in": {
                    "animation": "loading_1",
                    "cycles": 1
                }
            }
        }, {
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

try:
    with open('./config.json', 'r') as input_file:
        config.update(json.load(input_file))
except Exception as error:
    print_traceback(error)
