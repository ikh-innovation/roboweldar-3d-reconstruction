import sys
import os

from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parents[1]))
# sys.path.append(os.path.join(str(Path(os.path.abspath(__file__)).parents[1]), "src"))
# sys.path.append(os.path.join(str(Path(os.path.abspath(__file__)).parents[1]), "src","rest"))

# TODO: fix import error
# TODO: run testing pipeline
# TODO: use pytest-order - a pytest plugin to order test execution

from src.rest.client import clean_up_folder

from test.src.client_utils import send_dummy_files

import filecmp
import subprocess
import time
import pytest

from config import SERVER_DIR, ROOT_DIR, SERVER_UPLOADS_DIR


# start server

# start client

# run client_utils.py

# perform diff between files on output dir and expected dir when i know files have been generated


def is_mesh_files_exist():
    return os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.obj")) and os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.mtl")) and os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texture_1001.png"))


def is_transformed_mesh_files_exist():
    return os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.obj")) and os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.mtl")) and os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh_0.png"))


def test_client():
    print("Cleaning up folders...")
    clean_up_folder(os.path.join(SERVER_UPLOADS_DIR, "mesh"))
    clean_up_folder(os.path.join(ROOT_DIR, "reconstruction_data", "output"))

    myenv = os.environ.copy()
    # myenv['PATH'] = self._path_to_meshroom_bin  # visible in this process + all children
    # myenv['LD_LIBRARY_PATH'] = self._path_to_meshroom_lib  # v
    print("Running yarn install...")
    process = subprocess.call(["yarn", "install"], env=myenv,
                              # shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # preexec_fn=os.setsid,
                              cwd=SERVER_DIR)
    print("Running yarn start...")
    process = subprocess.call(["yarn", "start"], env=myenv,
                              # shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # preexec_fn=os.setsid,
                              cwd=SERVER_DIR)
    print("Uploading files to server...")

    send_dummy_files("cache_images", "localhost")  # upload test images to server

    print("Checking existence of mesh files...")

    while not is_mesh_files_exist():
        time.sleep(2)
    print("Checking existence of transformed mesh files...")

    while not is_transformed_mesh_files_exist():
        time.sleep(2)

    assert is_mesh_files_exist()
    assert is_transformed_mesh_files_exist()
