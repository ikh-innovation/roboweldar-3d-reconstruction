import glob
import sys
import os

from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parents[1]))
# sys.path.append(os.path.join(str(Path(os.path.abspath(__file__)).parents[1]), "src"))
# sys.path.append(os.path.join(str(Path(os.path.abspath(__file__)).parents[1]), "src","rest"))

# TODO: debug transformation stage (ln 103) - not working currently

from src.rest.client import clean_up_folder, main

from test.client_utils import send_dummy_files

import subprocess
import time

from config import SERVER_DIR, ROOT_DIR, SERVER_UPLOADS_DIR, CACHE_DIR, OUTPUT_DIR, TRANSFORMED_MESH_DIR


# start server

# start client

# run client_utils.py

# perform diff between files on output dir and expected dir when i know files have been generated


def is_mesh_files_exist_in_cache_dir():
    return os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.obj")) and os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.mtl")) and os.path.isfile(
        os.path.join(ROOT_DIR, "reconstruction_data", "output", "texture_1001.png"))


def is_transformed_mesh_files_exist_on_server_dir():
    return os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.obj")) and os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.mtl")) and os.path.isfile(
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh_0.png"))


def is_transformed_mesh_files_exist_in_dir():
    return os.path.isfile(
        os.path.join(TRANSFORMED_MESH_DIR,  "transformed_mesh.obj")) and os.path.isfile(
        os.path.join(TRANSFORMED_MESH_DIR,  "transformed_mesh.mtl")) and os.path.isfile(
        os.path.join(TRANSFORMED_MESH_DIR,  "transformed_mesh_0.png"))


def test_sfm_integration():

    myenv = os.environ.copy()

    print("Running yarn install...")
    process1 = subprocess.call(["yarn", "install"], env=myenv,
                               # shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # preexec_fn=os.setsid,
                               cwd=SERVER_DIR)
    print("Running yarn start...")

    process2 = subprocess.Popen(["yarn", "start"], env=myenv,
                                # shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # preexec_fn=os.setsid,
                                cwd=SERVER_DIR)
    print("Started server with PID {}".format(process2.pid))

    print("Cleaning up lingering server uploads in {}...".format(os.path.join(SERVER_UPLOADS_DIR)))
    clean_up_folder(os.path.join(SERVER_UPLOADS_DIR, "mesh"))
    clean_up_folder(os.path.join(SERVER_UPLOADS_DIR, "images"))
    clean_up_folder(os.path.join(SERVER_UPLOADS_DIR, "welding_trajectory"))
    print("Cleanup done...")

    time.sleep(4)

    print("Start SfM client")
    process3 = subprocess.Popen(["python", os.path.join(ROOT_DIR, "src", "rest", "client.py"), "--host", "localhost"],
                                env=myenv,
                                # shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # preexec_fn=os.setsid,
                                cwd=ROOT_DIR)

    print("Started SfM client with PID {}".format(process3.pid))

    time.sleep(4)

    print("Uploading files from test data dir to server images dir...")

    send_dummy_files("cache_images", "localhost")  # upload test images to server
    print("Uploaded files to server...")

    print("Started 3D reconstruction")

    print("Waiting for photogrammetry pipeline to finish...")

    while not is_mesh_files_exist_in_cache_dir():
        time.sleep(2)

    print("Waiting for mesh transformation pipeline to finish...")

    while not is_transformed_mesh_files_exist_in_dir():
        time.sleep(2)



    process3.kill()
    process2.kill()

    assert is_mesh_files_exist_in_cache_dir()
    assert is_transformed_mesh_files_exist_in_dir()


if __name__ == '__main__':
    test_sfm_integration()
