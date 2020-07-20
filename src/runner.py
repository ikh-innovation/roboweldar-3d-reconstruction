import threading
import time
import logging

from src.reconstruction import reconstruct, ThreeDReconstruction

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )


def reconstruction():
    logging.debug("Starting")
    reconstruct()
    logging.debug('Exiting')


def rest():
    logging.debug('Starting')
    time.sleep(5)
    ThreeDReconstruction.stop()
    logging.debug('Exiting')


if __name__ == '__main__':
    t = threading.Thread(name='non-daemon', target=reconstruction)

    d = threading.Thread(name='daemon', target=rest)
    d.setDaemon(True)

    d.start()
    t.start()
