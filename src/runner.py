import os
import threading
import time
import logging
from typing import List, Optional

import coloredlogs

from config import ROOT_DIR
from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.scheduler import batch_parse_logs
from src.reconstruction.reconstruction import reconstruct, ThreeDReconstruction

# create logger with 'spam_application'
logger = logging.getLogger("3d-reconstruction-service")
coloredlogs.install(level='DEBUG', logger=logger)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('3D-reconstruction-scheduler.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


class SharedData:
    def __init__(self, logs: Optional[List[ReconstructionStep]]):
        self._logs = logs

    @property
    def logs(self):
        return self._logs

    @logs.setter
    def logs(self, logs: List[ReconstructionStep]):
        self._logs = logs


def reconstruction():
    # this thread will run the 3d reconstruction using a subprocess call
    logger.info("Running Meshroom...")

    threedreconstruction = ThreeDReconstruction(
        path_to_meshroom_root=os.path.join(ROOT_DIR, "deps", "Meshroom-2019.2.0"),
        path_to_images_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "raw"),
        path_to_output_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "output"),
        path_to_cache_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "cache")
    )
    output = 1
    try:
        output = threedreconstruction.start()
    except Exception as err:
        logger.error(err)

    logger.debug("Exiting Meshroom...")
    return output


def log_parsing(shared_data: SharedData):
    # this thread will do the log parsing, and conversion into an appropriate data model
    logger.info("Starting Meshroom log parsing...")
    while True:
        try:
            shared_data.logs = batch_parse_logs(path_to_cache_dir="/home/orfeas/Documents/Code/roboweldar/" \
                                                                  "roboweldar-3d-reconstruction/test/box_reconstruction/cache")
            time.sleep(5)
        except Exception as err:
            logger.error(msg=err)
            break

    logger.info("Exiting Meshroom log parsing...")


def rest(shared_data: SharedData):
    # this thread will do the request posting to Orion
    logging.debug("Starting REST service...")
    if shared_data.logs:
        for step in shared_data.logs:
            logger.info("Sending mock POST request with data: {}".format(step))
            time.sleep(5)
    logging.debug("Exiting REST service...")


if __name__ == '__main__':
    shared_data = SharedData(None)

    rec = threading.Thread(name='non-daemon', target=reconstruction)
    rest = threading.Thread(name='daemon', target=rest, args=(shared_data,))
    logparser = threading.Thread(name='daemon', target=log_parsing, args=(shared_data,))
    rest.setDaemon(True)

    rec.start()
    logparser.start()
    rest.start()
