import os
import threading
import time
import logging
from typing import List, Optional

import coloredlogs

from config import ROOT_DIR
from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.scheduler import batch_parse_logs
from src.logging_config import ColorFormatter
from src.reconstruction.reconstruction import reconstruct, ThreeDReconstruction

formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("3d-reconstruction-service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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
        logger.error(err, exc_info=1)

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
        except FileNotFoundError as err:
            logger.error(msg=err)
            continue
        except Exception as err:
            logger.error(msg=err)
            break

    logger.info("Exiting Meshroom log parsing...")


def post_updates(shared_data: SharedData):
    # this thread will do the request posting to Orion
    logging.debug("Starting REST service...")
    while True:
        try:
            if shared_data.logs:
                for step in shared_data.logs:
                    logger.info("Sending mock POST request with data: {}".format(step))
                    # TODO: Need to create a REST service that sends updates to the Context Broker
            time.sleep(5)
        # except FileNotFoundError as err:
        #     logger.error(msg=err)
        #     continue
        except Exception as err:
            logger.error(msg=err)
            break

    logging.debug("Exiting REST service...")


if __name__ == '__main__':
    shared_data = SharedData(None)

    reconstruction_thread = threading.Thread(name='non-daemon', target=reconstruction)

    # rest and log-parsing threads run infinitely and does not exit on its own, so it should be run in a daemonic thread
    update_thread = threading.Thread(name='daemon', target=post_updates, args=(shared_data,))
    logparser_thread = threading.Thread(name='daemon', target=log_parsing, args=(shared_data,))

    reconstruction_thread.start()
    logparser_thread.start()
    update_thread.start()
