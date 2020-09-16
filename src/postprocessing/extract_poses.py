from typing import Dict

import simplejson as json
import glob
import os
import numpy as np


def extract_filename(path_to_file: str) -> str:
    return os.path.split(os.path.splitext(path_to_file)[0])[-1]


def load_computed_poses(path_to_cameras_sfm: str) -> Dict:
    with open(path_to_cameras_sfm) as jsonFile:
        report = json.load(jsonFile)

    d = {}

    poses = report["poses"]
    views = report["views"]
    poses_dict = {pose["poseId"]: pose for pose in poses}

    for view in views:
        filename = extract_filename(view["path"])
        try:
            d.update({filename: {
                "poseId": view["poseId"],
                "rotation": poses_dict[view["poseId"]]["pose"]["transform"]["rotation"],
                "center": poses_dict[view["poseId"]]["pose"]["transform"]["center"]}})
        except KeyError as err:
            print("Could not find poseId: {}".format(err))

    print("Loaded a total of {} computed camera poses...".format(len(views)))

    return d


def load_robot_poses(path_to_poses_dir: str) -> Dict:
    files = glob.glob(os.path.join(path_to_poses_dir, "*.npy"))
    rot_mats = {}
    for path_to_file in files:
        rot_mats.update({extract_filename(path_to_file): np.load(path_to_file)})
    print("Loaded a total of {} .npy files...".format(len(files)))
    return rot_mats


def impute_robot_poses(path_to_cameras_sfm: str, rot_mats: Dict, d: Dict):
    # assert sorted(d.keys()) == sorted(rot_mats.keys())
    new_d = {}

    for filename, pose in d.items():
        rotation_matrix = rot_mats[filename][:3, :3]
        position = rot_mats[filename][:3, 3]
        new_d.update({d[filename]["poseId"]: {"filename": filename, "rotation": rotation_matrix, "center": position}})

    with open(path_to_cameras_sfm, "r") as json_file:
        report = json.load(json_file)

    for pose in report["poses"]:
        pose["pose"]["transform"]["rotation"] = list(
            map(lambda x: str(x), new_d[pose["poseId"]]["rotation"].flatten().tolist()))
        pose["pose"]["transform"]["center"] = list(
            map(lambda x: str(x), new_d[pose["poseId"]]["center"].flatten().tolist()))
        pose["locked"] = 1

    json_file.close()

    with open(path_to_cameras_sfm + "_modified", "w") as json_file:
        json.dump(report, json_file, indent=4, sort_keys=True)


if __name__ == '__main__':
    path_to_cameras_sfm = "/mnt/storage/roboweldar/3dphotogrammetry_test_4/cameras.sfm"
    d = load_computed_poses(path_to_cameras_sfm)
    rot_mats = load_robot_poses(path_to_poses_dir="/mnt/storage/roboweldar/3dphotogrammetry_test_4/raw")
    impute_robot_poses(path_to_cameras_sfm, rot_mats, d)
