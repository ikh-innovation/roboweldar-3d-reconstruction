import subprocess
import os
import glob
from typing import List
import logging

logger = logging.getLogger("RoboWeldAR-3D-Reconstruction")

from config import ROOT_DIR


class ThreeDReconstruction:
    def __init__(self, path_to_meshroom_root: str, path_to_images_dir: str, path_to_output_dir: str,
                 path_to_cache_dir: str):
        self._path_to_meshroom_root = path_to_meshroom_root
        self._path_to_images_dir = path_to_images_dir
        self._path_to_output_dir = path_to_output_dir
        self._path_to_cache_dir = path_to_cache_dir

        assert os.path.isdir(self._path_to_meshroom_root)
        assert os.path.isdir(self._path_to_images_dir)
        assert os.path.isdir(self._path_to_output_dir)

        self._setup_paths()
        self._myenv = None
        self._set_environment_variables()

    def _setup_paths(self):
        self._path_to_meshroom_photogrammetry_bin = os.path.join(self._path_to_meshroom_root, "meshroom_photogrammetry")
        self._path_to_meshroom_lib = os.path.join(self._path_to_meshroom_root, "aliceVision", "lib")
        self._path_to_meshroom_bin = os.path.join(self._path_to_meshroom_root, "aliceVision", "bin")

    def _set_environment_variables(self):
        self._myenv = os.environ.copy()
        self._myenv['PATH'] = self._path_to_meshroom_bin  # visible in this process + all children
        self._myenv['LD_LIBRARY_PATH'] = self._path_to_meshroom_lib  # visible in this process + all children

    @property
    def path_to_meshroom_root(self):
        return self._path_to_meshroom_root

    @property
    def path_to_images_dir(self):
        return self._path_to_images_dir

    @property
    def path_to_output_dir(self):
        return self._path_to_output_dir

    @property
    def path_to_cache_dir(self):
        return self._path_to_cache_dir

    def start(self):
        try:
            subprocess.check_call([self._path_to_meshroom_photogrammetry_bin,
                                   "--input", self.path_to_images_dir,
                                   "--output", self.path_to_output_dir,
                                   "--cache", self.path_to_cache_dir,
                                   "--forceStatus"],
                                  env=self._myenv)
        except OSError:
            self.stop()

    @staticmethod
    def stop():
        try:
            subprocess.call("kill $(ps aux | grep '[m]eshroom' | awk '{print $2}')", shell=True)
        except subprocess.CalledProcessError as err:
            logger.error(
                "Tried to kill process. Returned error code: {} with message {}".format(err.returncode, err.output))


def reconstruct():
    threedreconstruction = ThreeDReconstruction(
        path_to_meshroom_root=os.path.join(ROOT_DIR, "deps", "Meshroom-2019.2.0"),
        path_to_images_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "raw"),
        path_to_output_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "output"),
        path_to_cache_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "cache")
    )

    threedreconstruction.start()

    # images = glob.glob(os.path.join(path_to_images, "*.JPG"))


if __name__ == '__main__':
    reconstruct()
