from uio import StringIO
import sys


def print_trace(error):
    buffer = StringIO()
    sys.print_exception(error, buffer)
    print(buffer.getvalue())
