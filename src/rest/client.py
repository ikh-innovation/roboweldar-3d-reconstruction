import ctypes
import hashlib
import logging
import os
import shutil
import signal
import threading
import glob
import time
from copy import deepcopy
from functools import partial
from typing import List, Dict, Optional
import numpy as np

import pyfiware
import requests
import simplejson as json
from pathlib import Path

from config import ROOT_DIR, IMAGES_DIR, OUTPUT_DIR, CACHE_DIR, MESHROOM_DIR, TRANSFORMED_MESH_DIR
from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.scheduler import batch_parse_logs
from src.logging_config import ColorFormatter
from src.postprocessing.transform_poses import transform_model_to_world_coordinates
from src.reconstruction.reconstruction import ThreeDReconstruction

# TODO: import the following from roboweldar-networking
from src.rest.fiware_client import post_entity_context_update, create_entity
from src.rest.roboweldar_networking.interfaces import ws_client
from src.rest.roboweldar_networking.interfaces.http_client import send_files

from src.rest.helpers import getFiles

from src.runner import SharedData, reconstruction, post_updates, log_parsing

# logging

logger = logging.getLogger("3d-reconstruction-service")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('web_service.log')
fh.setLevel(logging.DEBUG)
# log errors to stdout
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


class StoppingThread(threading.Thread):

    def __init__(self, name, shared_data):
        """ constructor, setting initial variables """
        self._stop_event = threading.Event()
        self._sleep_period = 1.0
        self.shared_data = shared_data

        threading.Thread.__init__(self, name=name)

    def run(self):
        """ Example main control loop """
        count = 0
        while not self._stop_event.isSet():
            count += 1
            self._stop_event.wait(self._sleep_period)

    def join(self, timeout=None):
        """ Stop the thread. """
        self._stop_event.set()
        print("set stop event")
        threading.Thread.join(self, timeout)


def clean_up_folder(path_to_dir: str):
    files = glob.glob(os.path.join(path_to_dir, "*"))
    for f in files:
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def create_folder(path_to_dir: str):
    if os.path.isdir(path_to_dir) or os.path.isfile(path_to_dir):
        pass
    else:
        os.mkdir(path_to_dir)


class ReconstructionThread(StoppingThread):
    def run(self):
        logger.debug("Starting Meshroom reconstruction thread...")

        # TODO: Provide links to images as arguments and download
        #  them to the "raw" dir prior to running further code

        # this thread will run the 3d reconstruction using a subprocess call
        logger.info("Running Meshroom...")

        # run SfM
        threedreconstruction = ThreeDReconstruction(
            path_to_meshroom_root=MESHROOM_DIR,
            path_to_images_dir=IMAGES_DIR,
            path_to_output_dir=OUTPUT_DIR,
            path_to_cache_dir=CACHE_DIR, )
        # If process returns exit code 0, it has completed successfully

        process = threedreconstruction.start()
        logger.info("After start!!!!!")

        # Get stuck in this loop until stopevent flag is set, otherwise reach end of execution and terminate thread
        while not self._stop_event.isSet():
            self._stop_event.wait(self._sleep_period)

        #######################################
        # Code for parsing STDOUT of process and logging it
        #
        # output = ""
        # for line in iter(process.stdout.readline, ""):
        #     logger.info(line)
        #     output += str(line)
        #
        # process.wait()
        # exit_code = process.returncode
        #
        # if exit_code == 0:
        #     return output
        # else:
        #     raise Exception(command, exit_code, output)
        #

        ######################################

        # If execution gets here before 3dreconstruction is finished, it kills the process

        # TODO: This works but should not kill process like that as it might kill other sessions on the server,
        #  unless dockerization is used for every client connection instance

        threedreconstruction.kill()

        logger.info("Exiting Meshroom reconstruction thread...")


class LogParserThread(StoppingThread):
    def run(self):
        # this thread will do the log parsing, and conversion into an appropriate data model
        logger.info("Starting Meshroom log parsing...")

        # while the stopflag is not set, keep parsing the logs generated by Meshroom
        while not self._stop_event.isSet():
            time.sleep(1.0)
            try:
                print("parsing...........")
                shared_data.logs = batch_parse_logs(
                    path_to_cache_dir=CACHE_DIR)
            except FileNotFoundError as err:
                logger.error(msg=err)
                continue
            except Exception as err:
                logger.error(msg=err)
                break

            self._stop_event.wait(self._sleep_period)

        logger.info("Exiting Meshroom log parsing...")


class UpdatesThread(StoppingThread):
    def run(self):

        logger.info("Starting update thread...")

        # while the stopflag is not set, keep posting updates to the Context Broker
        while not self._stop_event.isSet():
            try:
                if shared_data.logs:
                    for step in shared_data.logs:
                        logger.info("Sending mock POST request with data: {}".format(step))
                        # TODO: Need to create a REST service that sends updates to the Context Broker

            # except FileNotFoundError as err:
            #     logger.error(msg=err)
            #     continue
            except Exception as err:
                logger.error(msg=err)
                break

            self._stop_event.wait(self._sleep_period)

        logger.info("Stopping update thread...")


# Shared data between threads
shared_data = SharedData(None)
# Share threads among routes
threads = []

reconstruction_thread = ReconstructionThread(name="reconstruction_thread", shared_data=shared_data)
# rest and log-parsing threads run infinitely and does not exit on its own, so it should be run in a daemonic thread
post_updates_thread = UpdatesThread(name="post_updates_thread", shared_data=shared_data)
logparser_thread = LogParserThread(name="log_parsing_thread", shared_data=shared_data)


def construct_status_json(reconstruction_steps: List[ReconstructionStep]):
    # startedAt = min([step.datetime_start for step in reconstruction_steps if step.datetime_start])
    startedAt = None

    if all([step.status == "SUCCESS" for step in reconstruction_steps]):
        endedAt = max([step.datetime_end for step in reconstruction_steps])
    else:
        endedAt = None

    percentageOverallProgress = int((sum([step.status == "SUCCESS" for step in reconstruction_steps]) / len(
        reconstruction_steps)) * 100)

    inputFiles = None

    output_dir = os.path.join(reconstruction_steps[0].path_to_cache_dir, "Texturing")

    if len(os.listdir(output_dir)) == 0:
        outputFiles = None
    else:
        latest_output_dir = sorted(Path(output_dir).iterdir(), key=os.path.getmtime)[0]
        path_to_obj = glob.glob(os.path.join(latest_output_dir, "*.obj"))
        path_to_mtl = glob.glob(os.path.join(latest_output_dir, "*.mtl"))
        path_to_png = glob.glob(os.path.join(latest_output_dir, "*.png"))
        if len(path_to_obj) == 1 and len(path_to_mtl) == 1 and len(path_to_png) == 1:
            outputFiles = [path_to_obj[0], path_to_mtl[0], path_to_png[0]]
        else:
            outputFiles = None

    d = {
        "id": "StructureFromMotionService-{}".format(str(startedAt)),
        "type": "Computation",
        "address": {
            "addressLocality": "Athens",
            "addressCountry": "GR"
        },
        "inputFiles": inputFiles,
        "outputFiles": outputFiles,
        "dataProvider": "iKnowHow SA",
        "startedAt": str(startedAt),
        "endedAt": str(endedAt),
        "percentageOverallProgress": percentageOverallProgress,
        "children": [],
        "location": {
            "type": "Point",
            "coordinates": [
                -4.754444444,
                41.64833333
            ]
        }
    }

    for step in reconstruction_steps:
        b = {s: str(getattr(step, s, None)) for s in dir(step) if isinstance(getattr(type(step), s, None), property)}
        b["id"] = step.__class__.__name__
        d["children"].append(b)

    return d


def start():
    reconstruction_thread = ReconstructionThread(name="reconstruction_thread", shared_data=shared_data)
    # rest and log-parsing threads run infinitely and does not exit on its own, so it should be run in a daemonic thread
    post_updates_thread = UpdatesThread(name="post_updates_thread", shared_data=shared_data)
    logparser_thread = LogParserThread(name="log_parsing_thread", shared_data=shared_data)
    logparser_thread.start()
    threads.append(logparser_thread)
    reconstruction_thread.start()
    threads.append(reconstruction_thread)
    post_updates_thread.start()
    threads.append(post_updates_thread)
    message = "Started StructureFromMotion module..."
    print(message)

    return message


def stop():
    if len(threads) == 3:
        threads[2].join()
        threads[1].join()
        threads[0].join()

        # TODO: Clean all files after module is stopped
        return "Stopped StructureFromMotion module..."

    else:
        return "No running instance of StructureFromMotion module..."


def send_percentage_progress_to_server(ws):
    d = format_status_json()
    message = {'status': d["percentageOverallProgress"]}
    print(message)
    ws_client.send_message(ws, json.dumps(message))


def clean_up_data_model(data: Dict) -> Dict:
    data_modified = deepcopy(data)
    data_modified.pop("id", None)
    data_modified.pop("type", None)
    return data_modified


def format_status_json():
    if shared_data.logs:
        status = construct_status_json(shared_data.logs)
    else:
        status = {}
        status["percentageOverallProgress"] = 0.0
        status["outputFiles"] = None
    return status


def on_message(ws, message: str, host: str, port: str):
    d = json.loads(message)
    if d["message"] == "start":
        # get the images from the server
        print("Downloading images from the server ({}) to {}...".format(host, IMAGES_DIR))
        getFiles(host=host, httpPort=port, path_to_dir=IMAGES_DIR)

        print("Starting SfM...")

        start()
    elif d["message"] == "stop":
        print("Stopping SfM...")

        stop()


def wrap_send_images(route: str, output_files: List[str]) -> bool:
    try:
        send_files(route, output_files)
    except:
        pass
    else:
        return True


def is_output_files_valid(output_files: List[str]) -> bool:
    if output_files:
        is_valid = (os.path.split(output_files[0])[-1] == "texturedMesh.obj") and (
                os.path.split(output_files[1])[-1] == "texturedMesh.mtl") and (
                           os.path.split(output_files[2])[-1] == "texture_1001.png")
    else:
        is_valid = False

    return is_valid


def noop_fn(*args, **kwargs):
    pass


class FiwareConnector:
    def __init__(self, orion_cb_host: str, orion_cb_port: str,
                 entity_id: str,
                 element_type: str):
        self.oc: pyfiware.OrionConnector = []
        self.orion_cb_host = orion_cb_host
        self.orion_cb_port = orion_cb_port
        self.entity_id = entity_id
        self.element_type = element_type

        # if connection to Orion doesn't work, neutralize member functions to noops
        try:
            self.init_connection()
        except pyfiware.FiException as e:
            print(e)
            self.create_entity = noop_fn
            self.post_entity_context_update = noop_fn
        else:
            pass

    def init_connection(self):
        addr = "{}:{}".format(self.orion_cb_host, self.orion_cb_port)
        self.oc = pyfiware.OrionConnector(host=addr)
        res = requests.get("http://" + addr + "/version")
        if res.status_code != 200:
            raise pyfiware.FiException

    @staticmethod
    def create_entity(*args, **kwargs):
        create_entity(oc=kwargs["oc"],
                      entity_id=kwargs["entity_id"],
                      element_type=kwargs["element_type"],
                      data=kwargs["data"],
                      )

    @staticmethod
    def post_entity_context_update(*args, **kwargs):
        post_entity_context_update(oc=kwargs["oc"],
                                   entity_id=kwargs["entity_id"],
                                   element_type=kwargs["element_type"],
                                   data=clean_up_data_model(kwargs["data"]),
                                   )


def is_valid_orion_instance(orion_cb_host: Optional[str], orion_cb_port: Optional[str]) -> bool:
    pass
    # TODO: implement orion checking via IP and port (version number)
    return False


def main(roboweldar_server_host: str, endpoint_type: str, orion_cb_host: str="", orion_cb_port: str=""):
    is_fiware_enabled = False
    if is_valid_orion_instance(orion_cb_host, orion_cb_port):
        is_fiware_enabled = True

    # make sure dirs exist
    create_folder(IMAGES_DIR)
    create_folder(OUTPUT_DIR)
    create_folder(TRANSFORMED_MESH_DIR)
    create_folder(CACHE_DIR)

    # clean up directory
    clean_up_folder(IMAGES_DIR)
    clean_up_folder(OUTPUT_DIR)
    clean_up_folder(TRANSFORMED_MESH_DIR)
    clean_up_folder(CACHE_DIR)

    # init websocket client
    wsClient = ws_client.getClient("ws://" + roboweldar_server_host + ":3001/" + endpoint_type)
    wsClient.on_message = partial(on_message, host=roboweldar_server_host, port=3000)
    wst = threading.Thread(target=wsClient.run_forever)
    wst.daemon = True
    wst.start()

    # init Orion Context Broker
    if is_fiware_enabled:
        fiware_connector = FiwareConnector(
            orion_cb_host=orion_cb_host,
            orion_cb_port=orion_cb_port,
            entity_id="3DReconstructionService" + str(np.random.randint(1e12)),
            element_type="ComputationService",
        )
        fiware_connector.create_entity(oc=fiware_connector.oc,
                                       entity_id=fiware_connector.entity_id,
                                       element_type=fiware_connector.element_type,
                                       data=format_status_json(),
                                       )

    # start()
    running = True
    is_sent_images = False
    time.sleep(1)
    while (running):
        time.sleep(2)
        send_percentage_progress_to_server(wsClient)
        if is_fiware_enabled:
            fiware_connector.post_entity_context_update(oc=fiware_connector.oc,
                                                        entity_id=fiware_connector.entity_id,
                                                        element_type=fiware_connector.element_type,
                                                        data=clean_up_data_model(format_status_json()))
        outputFiles = format_status_json()["outputFiles"]
        print(format_status_json())
        print(outputFiles)
        if is_output_files_valid(outputFiles):
            print(outputFiles)

            if is_sent_images:
                pass
            else:

                # the folder StructureFromMotion may contain multiple subdirs if the reconstruction is run multiple times.
                # However, by erasing the dirs prior to starting the reconstruction, we guarantee that this wildcard
                # resolution always works
                path_to_cameras_sfm = glob.glob(os.path.join(CACHE_DIR, "StructureFromMotion", "*", "cameras.sfm"))[0]

                # Perform trasnformation of model from arbitrary Meshroom coordinates to World coordinates
                transform_model_to_world_coordinates(
                    path_to_poses_dir=IMAGES_DIR,
                    path_to_cameras_sfm=path_to_cameras_sfm,
                    path_to_computed_mesh=outputFiles[0],
                    path_to_transformed_mesh_dir=TRANSFORMED_MESH_DIR,
                    show_plot=False
                )

                # change var outputFiles to point to transformed model
                outputFiles = [
                    os.path.join(TRANSFORMED_MESH_DIR, "transformed_mesh.obj"),
                    os.path.join(TRANSFORMED_MESH_DIR, "transformed_mesh.mtl"),
                    os.path.join(TRANSFORMED_MESH_DIR, "transformed_mesh_0.png"),
                ]
                print(outputFiles)
                url = "http://" + str(roboweldar_server_host) + ":3000/cache_mesh"
                print("Uploading 3D mesh files to {}...".format(url))
                is_sent_images = wrap_send_images(url, outputFiles)
                print("Uploaded 3D mesh files to {}...".format(url))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True,
                        help="Host on which the roboweldar server is running")
    parser.add_argument('--orion_cb_host', required=False,
                        help="Host on which the Orion Context Broker is running")
    parser.add_argument('--orion_cb_port', required=False,
                        help="Port on which the Orion Context Broker is running")

    args = parser.parse_args()
    main(roboweldar_server_host=args.host, endpoint_type="sfm", orion_cb_host=args.orion_cb_host,
         orion_cb_port=args.orion_cb_port)
