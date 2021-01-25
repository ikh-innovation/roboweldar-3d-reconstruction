import filecmp
import os

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(os.path.abspath(__file__)).parents[1]))
from config import TEST_DIR, ROOT_DIR, SERVER_UPLOADS_DIR


def test_obj():
    assert filecmp.cmp(os.path.join(TEST_DIR, "box_reconstruction", "output", "mesh", "texturedMesh.obj"),
                       os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.obj"))


def test_mtl():
    assert filecmp.cmp(os.path.join(TEST_DIR, "box_reconstruction", "output", "mesh", "texturedMesh.mtl"),
                       os.path.join(ROOT_DIR, "reconstruction_data", "output", "texturedMesh.mtl"))


def test_png():
    assert filecmp.cmp(os.path.join(TEST_DIR, "box_reconstruction", "output", "mesh", "texture_1001.png"),
                       os.path.join(ROOT_DIR, "reconstruction_data", "output", "texture_1001.png"))


def test_transformed_obj():
    assert filecmp.cmp(
        os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformed_mesh.obj"),
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.obj"))


def test_transformed_mtl():
    assert filecmp.cmp(
        os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformed_mesh.mtl"),
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh.mtl"))


def test_transformed_png():
    assert filecmp.cmp(
        os.path.join(TEST_DIR, "box_reconstruction", "output", "transformed_mesh", "transformed_mesh_0.png"),
        os.path.join(SERVER_UPLOADS_DIR, "mesh", "transformed_mesh_0.png"))
