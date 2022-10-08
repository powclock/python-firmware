import time
from config import config


def get_time_text():
    current_time = time.gmtime(time.time())

    hour = str((current_time[3] + config['utc_offset']) % 24)
    if len(hour) == 1:
        hour = '0' + hour

    minutes = str(current_time[4])
    if len(minutes) == 1:
        minutes = '0' + minutes

    return f'{hour} {minutes}'
