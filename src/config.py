import ujson as json
from utils import print_traceback

DEFAULT_CONFIG = {
    "update": {
        "enabled": True,
        "url": "https://raw.githubusercontent.com",
        "repo": "powclock/firmware-python",
        "branch": "master",
        "descriptor": "update.json",
    },
    "utc_offset": 1,
    "display_ip":  True,
    "cycles_to_update": 3,
    "sources": {
        "powclock_api": {
            "url": "http://api.powclock.com/v1",
            "method": "get",
            "attributes": {
                "price": [
                    "price",
                    "usd"
                ],
                "height": []
            }
        }
    },
    "slides": [
        {
            "message": "{time}",
            "millis": 6000
        },
        {
            "message": "usd",
            "millis": 2000
        },
        {
            "source": "powclock_api",
            "message": "{price}",
            "animations": {
                "up": "trending_up_1",
                "down": "trending_down_1"
            },
            "millis": 6000
        },
        {
            "message": "sats",
            "millis": 2000
        },
        {
            "source": "powclock_api",
            "message": "int(1e8/{price})",
            "animations": {
                "up": "trending_up_1",
                "down": "trending_down_1"
            },
            "millis": 6000
        },
        {
            "message": "height",
            "millis": 2000
        },
        {
            "source": "powclock_api",
            "message": "{height}",
            "millis": 6000
        }
    ],
    "animations": {
        "trending_up_1": {
            "messages": [
                "     ⬇  ",
                "      - ",
                "       ⬆"
            ],
            "millis": 100
        },
        "trending_down_1": {
            "messages": [
                "     ⬆  ",
                "      - ",
                "       ⬇"
            ],
            "millis": 100
        },
        "loading_1": {
            "messages": [
                "↙       ",
                "↖       ",
                "⬆       ",
                " ⬆      ",
                "  ⬆     ",
                "   ⬆    ",
                "    ⬆   ",
                "     ⬆  ",
                "      ⬆ ",
                "       ⬆",
                "       ↗",
                "       ↘",
                "       ⬇",
                "      ⬇ ",
                "     ⬇  ",
                "    ⬇   ",
                "   ⬇    ",
                "  ⬇     ",
                " ⬇      ",
                "⬇       "
            ],
            "millis": 15
        },
        "loading_2": {
            "messages": [
                "↙       ",
                "↖       ",
                "⬆       ",
                " ⬆      ",
                "  ⬆     ",
                "   ⬆    ",
                "   ↗    ",
                "    ↙   ",
                "    ⬇   ",
                "     ⬇  ",
                "      ⬇ ",
                "       ⬇",
                "       ↘",
                "       ↗",
                "       ⬆",
                "      ⬆ ",
                "     ⬆  ",
                "    ⬆   ",
                "    ↖   ",
                "   ↘    ",
                "   ⬇    ",
                "  ⬇     ",
                " ⬇      ",
                "⬇       "
            ],
            "millis": 15
        }
    }
}


config = DEFAULT_CONFIG
try:
    with open('config.json', 'r') as input_file:
        config.update(json.load(input_file))
except Exception as error:
    print_traceback(error)
