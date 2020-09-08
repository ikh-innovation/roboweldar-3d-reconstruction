import inspect
import os
import glob
import simplejson as json
from typing import Dict
import datetime as dt

import logging

from config import ROOT_DIR, LOGGING_ENABLED

from src.logging_config import ColorFormatter
from src.noop_logger import NoopLogger

if LOGGING_ENABLED:
    formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # this handler will write to sys.stderr by default
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    # adding handler to our logger
    logger = logging.getLogger("3d-reconstruction-service.log_parser")
    logger.addHandler(handler)
else:
    logger = NoopLogger()


class LogParser:
    def __init__(self, path_to_cache_dir: str):
        self.path_to_cache_dir = path_to_cache_dir

    @staticmethod
    def parse(path_to_cache_dir: str, step_id: str) -> Dict:
        path_to_status = glob.glob(os.path.join(path_to_cache_dir, step_id, "**", "*status*"), recursive=True)

        if len(path_to_status) == 0:
            raise FileNotFoundError(
                "No status file found for ReconstructionStep {}. Are you sure the process has reached that step?".format(
                    step_id))
        else:
            latest_file = max(path_to_status, key=os.path.getctime)

        logger.info("Found status file: {}".format(latest_file))

        if os.path.isfile(latest_file):
            with open(latest_file, "r") as infile:
                data = infile.readlines()
                data = "".join(data)
                jsonified = json.loads(data)
                logger.info("Jsonified file contents: {}".format(jsonified))
                return jsonified


class ReconstructionStep:
    def __init__(self, path_to_cache_dir: str):
        self._step_id = self.__class__.__name__
        self._path_to_cache_dir = path_to_cache_dir

        self._status = None
        self._datetime_start = None
        self._datetime_end = None
        self._datetime_elapsed = None
        self._parsed_log = self._parse_log()

        self._populate_attributes()

    def _parse_log(self) -> Dict:
        return LogParser.parse(path_to_cache_dir=self.path_to_cache_dir,
                               step_id=self._step_id)

    def _populate_attributes(self):
        self._status = self._parsed_log["status"]
        if self.status == "SUCCESS":
            self._datetime_start = dt.datetime.strptime(self._parsed_log["startDateTime"], '%Y-%m-%d %H:%M:%S.%f')
            self._datetime_end = dt.datetime.strptime(self._parsed_log["endDateTime"], '%Y-%m-%d %H:%M:%S.%f')
            self._datetime_elapsed = dt.datetime.strptime(self._parsed_log["elapsedTimeStr"],
                                                          "%H:%M:%S.%f") - dt.datetime(
                1900, 1, 1)

    @property
    def path_to_cache_dir(self):
        return self._path_to_cache_dir

    @property
    def status(self):
        return self._status

    @property
    def datetime_start(self) -> dt.datetime:
        return self._datetime_start

    @property
    def datetime_end(self) -> dt.datetime:
        return self._datetime_end

    @property
    def datetime_elapsed(self) -> dt.timedelta:
        return self._datetime_elapsed

    def __repr__(self):
        class_name = self.__class__.__name__
        members = ", ".join(["{} = {}".format(property_name, getattr(self, property_name))
                             for (property_name, property_value) in
                             inspect.getmembers(self.__class__, lambda x: isinstance(x, property))])
        # alternative implementation to get property names
        # property_names = [p for p in dir(self.__class__) if isinstance(getattr(self.__class__, p), property)]

        return "{}({})".format(class_name, members)

