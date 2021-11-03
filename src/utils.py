import sys
from uio import StringIO
import urequests as requests


def print_traceback(error):
    buffer = StringIO()
    sys.print_exception(error, buffer)
    print(buffer.getvalue())


def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception
