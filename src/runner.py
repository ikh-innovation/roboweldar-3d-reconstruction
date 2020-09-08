import glob
import os
import threading
import time
import logging
from typing import List, Optional

import coloredlogs

from config import ROOT_DIR, MESHROOM_DIR, IMAGES_DIR, OUTPUT_DIR, CACHE_DIR, LOGGING_ENABLED
from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.scheduler import batch_parse_logs
from src.logging_config import ColorFormatter
from src.noop_logger import NoopLogger
from src.reconstruction.reconstruction import reconstruct, ThreeDReconstruction

if LOGGING_ENABLED:
    formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger("3d-reconstruction-service")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
else:
    logger = NoopLogger()


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

    # clean up directory
    # clean_up_folder()

    # run SfM
    threedreconstruction = ThreeDReconstruction(
        path_to_meshroom_root=MESHROOM_DIR,
        path_to_images_dir=IMAGES_DIR,
        path_to_output_dir=OUTPUT_DIR,
        path_to_cache_dir=CACHE_DIR,
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
            shared_data.logs = batch_parse_logs(path_to_cache_dir=CACHE_DIR)
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
