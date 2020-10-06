import signal
import subprocess
import os
import glob
from time import sleep
from typing import List
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
    logger = logging.getLogger("3d-reconstruction-service.reconstruction")
    logger.addHandler(handler)
else:
    logger = NoopLogger()

from config import ROOT_DIR, LOGGING_ENABLED


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
        self._process = None

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
        command = [self._path_to_meshroom_photogrammetry_bin,
                   "--input", self.path_to_images_dir,
                   "--output", self.path_to_output_dir,
                   "--cache", self.path_to_cache_dir,
                   "--forceStatus"]

        # TODO: add argument "--pipeline MESHROOM_FILE" to improve reconstruction
        # https://github.com/alicevision/meshroom/issues/683

        # TODO: Need to check whether this command spawns other processes that need to be killed in case of exception



        self._process = subprocess.Popen(command,
                                         env=self._myenv,
                                         # shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         # preexec_fn=os.setsid,
                                         )

    # @staticmethod
    # def stop(pid):
    #     try:
    #         subprocess.call("kill {}".format(pid))
    #         # TODO: add return statement?
    #     except subprocess.CalledProcessError as err:
    #         logger.error(
    #             "Tried to kill process. Returned error code: {} with message {}".format(err.returncode, err.output))

    def stop(self):
        # os.killpg(os.getpgid(pid), signal.SIGTERM)
        self._process.terminate()
        self._process.kill()

    @staticmethod
    def kill():
        try:
            subprocess.call("kill $(ps aux | grep '[a]liceVision' | awk '{print $2}')", shell=True)
            # TODO: add return statement?
        except subprocess.CalledProcessError as err:
            logger.error(
                "Tried to kill process. Returned error code: {} with message {}".format(err.returncode, err.output))

        try:
            subprocess.call("kill $(ps aux | grep '[m]eshroom' | awk '{print $2}')", shell=True)
            # TODO: add return statement?
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
    threedreconstruction = ThreeDReconstruction(
        path_to_meshroom_root=os.path.join(ROOT_DIR, "deps", "Meshroom-2019.2.0"),
        path_to_images_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "raw"),
        path_to_output_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "output"),
        path_to_cache_dir=os.path.join(ROOT_DIR, "test", "box_reconstruction", "cache")
    )

    threedreconstruction.start()
    print(threedreconstruction._process.pid)

    sleep(6)

    # This does not work because the process spawns children
    threedreconstruction.stop()

    # TODO: This works but should not kill process like that as it might kill other sessions on the server
    threedreconstruction.kill()

