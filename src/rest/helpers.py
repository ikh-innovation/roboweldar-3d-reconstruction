import os

from src.rest.roboweldar_networking.interfaces import http_client


def getFiles(host, httpPort, path_to_dir):
    images = http_client.get_filenames('http://' + str(host) + ':' + str(httpPort) + '/' + 'image_names')
    print(images)
    for image in images:
        url = 'http://' + str(host) + ':' + str(httpPort) + '/serve_image?name=' + str(image)
        content = http_client.download_file(url)
        path_to_image = os.path.join(path_to_dir, str(image))
        with open(path_to_image, 'wb') as f:
            print("Writing image: {}".format(path_to_image))
            f.write(content)
