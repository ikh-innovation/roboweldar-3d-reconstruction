import os
import glob
import simplejson as json
from typing import Dict
import datetime as dt

from config import ROOT_DIR


class LogParser:
    def __init__(self, path_to_cache_dir: str):
        self.path_to_cache_dir = path_to_cache_dir

    @staticmethod
    def parse(path_to_cache_dir: str, step_id: str) -> Dict:
        path_to_status = glob.glob(os.path.join(path_to_cache_dir, step_id, "**", "*status*"), recursive=True)
        if isinstance(path_to_status, list):
            latest_file = max(path_to_status, key=os.path.getctime)
        else:
            latest_file = path_to_status[0]

        if os.path.isfile(latest_file):
            with open(latest_file, "r") as infile:
                data = infile.readlines()
                data = "".join(data)
                jsonified = json.loads(data)
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
        self._datetime_start = dt.datetime.strptime(self._parsed_log["startDateTime"], '%Y-%m-%d %H:%M:%S.%f')
        self._datetime_end = dt.datetime.strptime(self._parsed_log["endDateTime"], '%Y-%m-%d %H:%M:%S.%f')
        self._datetime_elapsed = dt.datetime.strptime(self._parsed_log["elapsedTimeStr"], "%H:%M:%S.%f") - dt.datetime(
            1900, 1, 1)
        self._status = self._parsed_log["status"]

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


if __name__ == '__main__':
    LogParser.parse("/home/orfeas/Documents/Code/roboweldar/roboweldar-3d-reconstruction/test/box_reconstruction/cache",
                    "CameraInit")
