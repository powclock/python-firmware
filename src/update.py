from config import config
import ujson as json
from os import remove, listdir, rename
from utils import download_file


def update_firmware():
    # Try to restore a bad update
    for file_name in listdir():
        if file_name[0] == ('_'):
            rename(file_name, file_name[1:])

    url = config['update']['url']
    repo = config['update']['repo']
    branch = config['update']['branch']
    descriptor = config['update']['descriptor']
    base_url = url + '/' + repo + '/' + branch

    # Download the descriptor
    content = download_file(base_url + '/' + descriptor)
    update_info = json.loads(content)

    # Download the files
    for file_path in update_info['replace']:
        content = download_file(base_url + '/' + file_path)
        filename = '_' + file_path.split('/')[-1]
        with open(filename, 'wb') as output_file:
            output_file.write(content)

    files_to_persist = set(
        [file_name for file_name in update_info['persist']])

    # Update files
    for file_name in listdir():
        if file_name not in files_to_persist and file_name[0] != ('_'):
            remove(file_name)
    for file_name in listdir():
        if file_name[0] == ('_'):
            rename(file_name, file_name[1:])
