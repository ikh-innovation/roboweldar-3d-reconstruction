import threading
import time
import logging

from src.reconstruction import reconstruct, ThreeDReconstruction

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )


def reconstruction():
    # this thread will run the 3d reconstruction using a subprocess call
    logging.debug("Starting")
    reconstruct()
    logging.debug('Exiting')


def log_parsing():
    # this thread will do the log parsing, and conversion into an appropriate data model
    logging.debug('Starting')
    time.sleep(5)
    logging.debug('Exiting')


def rest():
    # this thread will do the request posting to Orion
    logging.debug('Starting')
    time.sleep(5)
    ThreeDReconstruction.stop()
    logging.debug('Exiting')


if __name__ == '__main__':
    t = threading.Thread(name='non-daemon', target=reconstruction)
    d = threading.Thread(name='daemon', target=rest)
    l = threading.Thread(name='daemon', target=log_parsing)
    d.setDaemon(True)

    d.start()
    t.start()
    l.start()
