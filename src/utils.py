import sys
from uio import StringIO
import urequests as requests


def print_traceback(error):
    traceback_buffer = StringIO()
    sys.print_exception(error, traceback_buffer)
    print(traceback_buffer.getvalue())


def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError


def url_decode(input):
    output = input

    output = output.replace('%C2%Bf', '¿')
    output = output.replace('%C2%A1', '¡')

    output = output.replace('%C3%A1', 'á')
    output = output.replace('%C3%A9', 'é')
    output = output.replace('%C3%AD', 'í')
    output = output.replace('%C3%B3', 'ó')
    output = output.replace('%C3%BA', 'ú')
    output = output.replace('%C3%81', 'Á')
    output = output.replace('%C3%89', 'É')
    output = output.replace('%C3%8D', 'Í')
    output = output.replace('%C3%93', 'Ó')
    output = output.replace('%C3%9A', 'Ú')
    output = output.replace('%C3%A7', 'ç')
    output = output.replace('%C3%87', 'Ç')
    output = output.replace('%C3%B1', 'ñ')
    output = output.replace('%C3%91', 'Ñ')
    output = output.replace('%C3%A0', 'à')
    output = output.replace('%C3%A8', 'è')
    output = output.replace('%C3%AC', 'ì')
    output = output.replace('%C3%B2', 'ò')
    output = output.replace('%C3%B9', 'ù')
    output = output.replace('%C3%80', 'À')
    output = output.replace('%C3%88', 'È')
    output = output.replace('%C3%8C', 'Ì')
    output = output.replace('%C3%92', 'Ò')
    output = output.replace('%C3%99', 'Ù')
    output = output.replace('%C3%A2', 'â')
    output = output.replace('%C3%AA', 'ê')
    output = output.replace('%C3%AE', 'î')
    output = output.replace('%C3%B4', 'ô')
    output = output.replace('%C3%BB', 'û')
    output = output.replace('%C3%82', 'Â')
    output = output.replace('%C3%8A', 'Ê')
    output = output.replace('%C3%8E', 'Î')
    output = output.replace('%C3%94', 'Ô')
    output = output.replace('%C3%9B', 'Û')
    output = output.replace('%C3%A4', 'ä')
    output = output.replace('%C3%AB', 'ë')
    output = output.replace('%C3%AF', 'ï')
    output = output.replace('%C3%B6', 'ö')
    output = output.replace('%C3%BC', 'ü')
    output = output.replace('%C3%84', 'Ä')
    output = output.replace('%C3%8B', 'Ë')
    output = output.replace('%C3%8F', 'Ï')
    output = output.replace('%C3%96', 'Ö')
    output = output.replace('%C3%9C', 'Ü')
    output = output.replace('%C3%A3', 'ã')
    output = output.replace('%C3%B5', 'õ')
    output = output.replace('%C3%83', 'Ã')
    output = output.replace('%C3%95', 'Õ')
    output = output.replace('%C3%A5', 'å')
    output = output.replace('%C3%85', 'Å')
    output = output.replace('%C3%B8', 'ø')
    output = output.replace('%C3%98', 'Ø')
    output = output.replace('%C3%A6', 'æ')
    output = output.replace('%C3%86', 'Æ')
    output = output.replace('%C3%B0', 'ð')
    output = output.replace('%C3%90', 'Ð')
    output = output.replace('%C3%A8', 'è')
    output = output.replace('%C3%88', 'È')

    output = output.replace('%3A', ':')
    output = output.replace('%2F', '/')
    output = output.replace('%3F', '?')
    output = output.replace('%23', '#')
    output = output.replace('%5B', '[')
    output = output.replace('%5D', ']')
    output = output.replace('%40', '@')
    output = output.replace('%21', '!')
    output = output.replace('%24', '$')
    output = output.replace('%26', '&')
    output = output.replace('%27', "'")
    output = output.replace('%28', '(')
    output = output.replace('%29', ')')
    output = output.replace('%2A', '*')
    output = output.replace('%2B', '+')
    output = output.replace('%2C', ',')
    output = output.replace('%3B', ';')
    output = output.replace('%3D', '=')
    output = output.replace('%25', '%')
    output = output.replace('%20', ' ')
    output = output.replace('%5E', '^')
    output = output.replace('%60', '`')

    return output
