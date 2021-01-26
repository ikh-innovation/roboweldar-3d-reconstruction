import filecmp
import os

import sys
from pathlib import Path

from src.rest.client import create_folder

sys.path.append(str(Path(os.path.abspath(__file__)).parents[1]))

import pytest

from config import IMAGES_DIR, TEST_DIR
from src.postprocessing.transform_poses import transform_model_to_world_coordinates


def run_pipeline():
    create_folder(os.path.join(TEST_DIR, "tmp"))
    transform_model_to_world_coordinates(
        path_to_poses_dir=os.path.join(TEST_DIR, "box_reconstruction", "raw"),
        path_to_cameras_sfm=os.path.join(TEST_DIR, "box_reconstruction", "cameras", "cameras.sfm"),
        path_to_computed_mesh=os.path.join(TEST_DIR, "box_reconstruction", "output", "mesh", "texturedMesh.obj"),
        path_to_transformed_mesh_dir=os.path.join(TEST_DIR, "tmp"),
        show_plot=False
    )


def is_correct_transformed_obj() -> bool:
    return filecmp.cmp(
        os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformation_parameters.txt"),
        # expected result
        os.path.join(TEST_DIR, "tmp", "transformation_parameters.txt"))
#
#
# def is_correct_transformed_mtl() -> bool:
#     return filecmp.cmp(
#         os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformed_mesh.mtl"),
#         os.path.join(TEST_DIR, "tmp", "transformed_mesh.mtl"))
#
#
# def is_correct_transformed_png() -> bool:
#     return filecmp.cmp(
#         os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformed_mesh_0.png"),
#         os.path.join(TEST_DIR, "tmp", "transformed_mesh_0.png"))


def test_outputs():
    run_pipeline()
    assert is_correct_transformed_obj()
