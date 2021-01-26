import os

from config import TEST_DIR
from src.rest.roboweldar_networking.interfaces import http_client

httpPort = "3000"
wsPort = "3001"


def send_dummy_files(endpoint, host):
    # dummy data, files with those names should exist in this dir
    if endpoint == 'cache_images':
        filesNames = os.listdir(os.path.join(TEST_DIR, "box_reconstruction", "raw"))
        files = map(lambda fileName: os.path.join(TEST_DIR, "box_reconstruction", "raw", fileName), filesNames)
    elif endpoint == 'cache_mesh':
        filesNames = os.listdir('./mesh')
        files = map(lambda fileName: './mesh/' + fileName, filesNames)
    http_client.send_files('http://' + host + ':' + httpPort + '/' + endpoint, files)


if __name__ == '__main__':
    send_dummy_files("cache_images", "localhost")