from copy import deepcopy
from functools import partial

from scipy.optimize import minimize

from src.pose_input.extract_poses import load_robot_poses, load_computed_poses
import matplotlib.pyplot as plt
import numpy as np


class Pose:
    def __init__(self, id, pos_vec, rot_mat):
        self.id = id
        self.pos_vec = pos_vec
        self.rot_mat = rot_mat


def extract_robot_camera_poses(real_poses):
    poses = []
    for id, rm in real_poses.items():
        rot_mat = rm[:3, :3]
        pos_vec = np.array(rm[:3, 3]).reshape(3, 1)
        poses.append(Pose(id, pos_vec, rot_mat))
    return poses


def extract_inferred_camera_poses(computed_poses):
    poses = []
    for id, data in computed_poses.items():
        rot_mat = np.array(data["rotation"]).reshape(3, 3).astype("float")
        pos_vec = np.array(data["center"]).reshape(3, 1).astype("float")
        poses.append(Pose(id, pos_vec, rot_mat))
    return poses


def plot_camera_positions(ax, poses, color):
    for pose in poses:
        ax.scatter(pose.pos_vec[0], pose.pos_vec[1], pose.pos_vec[2], color=color)
    plt.axis("auto")


def plot_camera_poses(ax, poses, color):
    for pose in poses:
        ax.quiver(pose.pos_vec[0], pose.pos_vec[1], pose.pos_vec[2], pose.rot_mat[:, 0],
                  pose.rot_mat[:, 1], pose.rot_mat[:, 2], length=0.1,
                  normalize=True, color=color)
    plt.axis("auto")


def optimal_rotation(r_reals, r_computeds, Omega):
    l = []
    O = Omega.reshape(4, 4)
    O[2, 3] = 0.0
    O[3, 0:3] = 0.0
    O[3, 3] = 1.0
    print(O)
    for i, (r_real, r_computed) in enumerate(zip(r_reals, r_computeds)):
        l.append(np.linalg.norm(r_real - np.matmul(O, r_computed)))
    return np.sum(l)


def order_poses_by_id(poses):
    return sorted(poses, key=lambda x: x.id)


def optimize(real_poses, computed_poses):
    x0 = np.random.uniform(0, 1, [1, 16])
    ordered_real_poses = order_poses_by_id(real_poses)
    ordered_computed_poses = order_poses_by_id(computed_poses)
    r_reals = [np.concatenate([pose.pos_vec, np.array([[1]])]) for pose in ordered_real_poses]
    r_computeds = [np.concatenate([pose.pos_vec, np.array([[1]])]) for pose in ordered_computed_poses]
    partial_optimal_rotation = partial(optimal_rotation, r_reals, r_computeds)
    res = minimize(partial_optimal_rotation, x0, method='Nelder-Mead')
    Omega = np.array(res.x).reshape(4, 4)

    return Omega


def transform_computed_poses(Omega, computed_poses):
    l = []
    for pose in computed_poses:
        pose.pos_vec = np.matmul(Omega, np.concatenate([np.array(pose.pos_vec).reshape(3, 1), np.array([[1]])]))

    transformed_poses = computed_poses

    return transformed_poses


def main():
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    plot_func = plot_camera_positions

    real_poses = extract_robot_camera_poses(load_robot_poses(
        path_to_poses_dir="/mnt/storage/shared/roboweldar/new_dataset/new_dataset_reconstruction"))

    computed_poses = extract_inferred_camera_poses(load_computed_poses(
        path_to_cameras_sfm="/mnt/storage/roboweldar/simulation_test_1/MeshroomCache/StructureFromMotion/578f830addc4cce0c6fccaca48fd23068ffff1a3/cameras.sfm"))

    plot_func(ax, real_poses, 'r')
    plot_func(ax, computed_poses, 'g')

    Omega = optimize(real_poses, computed_poses)
    print(Omega)
    transformed_poses = transform_computed_poses(Omega, deepcopy(computed_poses))

    plot_func(ax, transformed_poses, 'b')
    plt.show()


if __name__ == '__main__':
    main()
