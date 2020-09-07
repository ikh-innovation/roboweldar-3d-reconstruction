from copy import deepcopy
from functools import partial

from scipy.optimize import minimize

from src.pose_input.extract_poses import load_robot_poses, load_computed_poses
import matplotlib.pyplot as plt
import numpy as np


def rotation_matrix_x(theta):
    return np.array(
        [[1, 0.0, 0.0],
         [0.0, np.cos(theta), -np.sin(theta)],
         [0.0, np.sin(theta), np.cos(theta)]]
    )


def rotation_matrix_y(theta):
    return np.array(
        [[np.cos(theta), 0.0, np.sin(theta)],
         [0.0, 1.0, 0.0],
         [-np.sin(theta), 0.0, np.cos(theta)]]
    )


def rotation_matrix_z(theta):
    return np.array(
        [[np.cos(theta), -np.sin(theta), 0.0],
         [np.sin(theta), np.cos(theta), 0.0],
         [0.0, 0.0, 1.0]]
    )


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


def optimal_translation(r_reals, r_computeds, r_estimate):
    l = []

    # print(r_estimate)
    for i, (r_real, r_computed) in enumerate(zip(r_reals, r_computeds)):
        l.append(np.linalg.norm(r_real - r_estimate))
    return np.sum(l)


def get_3d_rotation_matrix(alpha, beta, gamma):
    return rotation_matrix_x(alpha) @ rotation_matrix_y(beta) @ rotation_matrix_z(gamma)


def get_scaling_matrix(a, b, c):
    return np.array([
        [a, 0.0, 0.0],
        [0.0, b, 0.0],
        [0.0, 0.0, c], ]
    )


def optimal_rotation(r_reals, r_computeds, rotation_angles):
    l = []
    alpha, beta, gamma = rotation_angles[0], rotation_angles[1], rotation_angles[2]
    S = get_3d_rotation_matrix(alpha, beta, gamma)
    # print(S)
    for i, (r_real, r_computed) in enumerate(zip(r_reals, r_computeds)):
        l.append(np.linalg.norm(r_real - np.matmul(S, r_computed)))
    return np.sum(l)


def optimal_scaling(r_reals, r_computeds, scaling_factors):
    l = []
    a, b, c = scaling_factors[0], scaling_factors[1], scaling_factors[2]
    scaling = get_scaling_matrix(a, b, c)
    # print(scaling)
    for i, (r_real, r_computed) in enumerate(zip(r_reals, r_computeds)):
        l.append(np.linalg.norm(r_real - np.matmul(scaling, r_computed)))
    return np.sum(l)


def order_poses_by_id(poses):
    return sorted(poses, key=lambda x: x.id)


def optimize_rotation(real_poses, computed_poses):
    x0_Omega = np.random.uniform(-2 * np.pi, +2 * np.pi, [1, 3])
    ordered_real_poses = order_poses_by_id(real_poses)
    ordered_computed_poses = order_poses_by_id(computed_poses)

    print(compute_geometric_center(ordered_real_poses))
    print(compute_geometric_center(ordered_computed_poses))

    r_reals = [pose.pos_vec for pose in ordered_real_poses]
    r_computeds = [pose.pos_vec for pose in ordered_computed_poses]

    partial_func_optimal_rotation = partial(optimal_rotation, r_reals, r_computeds)
    res2 = minimize(partial_func_optimal_rotation, x0_Omega, method='Nelder-Mead', tol=1e-12)
    alpha = res2.x[0]
    beta = res2.x[1]
    gamma = res2.x[2]
    Omega = get_3d_rotation_matrix(alpha, beta, gamma)
    print(alpha, beta, gamma)

    return Omega


def optimize_scaling(real_poses, computed_poses):
    x0_scaling = np.random.uniform(-5, 5, [1, 3])
    ordered_real_poses = order_poses_by_id(real_poses)
    ordered_computed_poses = order_poses_by_id(computed_poses)

    # print(compute_geometric_center(ordered_real_poses))
    # print(compute_geometric_center(ordered_computed_poses))

    r_reals = [pose.pos_vec for pose in ordered_real_poses]
    r_computeds = [pose.pos_vec for pose in ordered_computed_poses]

    partial_func_optimal_scaling = partial(optimal_scaling, r_reals, r_computeds)
    res2 = minimize(partial_func_optimal_scaling, x0_scaling, method='Nelder-Mead', tol=1e-12)
    a = res2.x[0]
    b = res2.x[1]
    c = res2.x[2]

    # print(a, b, c)
    return get_scaling_matrix(a, b, c)


def transform_poses(scaling, Omega, r, poses):
    l = []
    for pose in poses:
        pose.pos_vec = pose.pos_vec - r
        pose.pos_vec = scaling @ Omega @ pose.pos_vec

    transformed_poses = poses

    return transformed_poses


def compute_geometric_center(poses):
    xs = np.mean([pose.pos_vec[0] for pose in poses])
    ys = np.mean([pose.pos_vec[1] for pose in poses])
    zs = np.mean([pose.pos_vec[2] for pose in poses])
    return np.array([xs, ys, zs]).reshape(3, 1)


def translate_poses(computed_poses, r_estimated):
    c = deepcopy(computed_poses)
    for pose in c:
        pose.pos_vec -= r_estimated

    return c


def check_omega(Omega: np.ndarray):
    print(np.matmul(Omega, np.transpose(Omega)))


def center_poses(poses):
    centroid = compute_geometric_center(poses)
    centered_poses = translate_poses(poses, centroid)
    return centered_poses, centroid


def pipeline(real_poses, computed_poses):
    centered_real_poses, real_centroid = center_poses(real_poses)
    centered_computed_poses, computed_centroid = center_poses(computed_poses)

    Omega = optimize_rotation(centered_real_poses, centered_computed_poses)
    check_omega(Omega)
    transformed_poses = transform_poses(scaling=np.identity(3), Omega=Omega, r=computed_centroid,
                                        poses=deepcopy(computed_poses))

    scaling = optimize_scaling(centered_real_poses, transformed_poses)

    doubly_transformed_poses = transform_poses(scaling=scaling, Omega=Omega, r=np.array([0.0, 0.0, 0.0]).reshape(3, 1),
                                               poses=deepcopy(transformed_poses))

    # rotate again

    Omega2 = optimize_rotation(centered_real_poses, doubly_transformed_poses)
    triply_transformed_poses = transform_poses(scaling=np.identity(3), Omega=Omega2, r=np.array([0.0, 0.0, 0.0]).reshape(3, 1),
                                        poses=deepcopy(doubly_transformed_poses))


    # scale again
    scaling2 = optimize_scaling(centered_real_poses, triply_transformed_poses)

    quadruply_transformed_poses = transform_poses(scaling=scaling2, Omega=np.identity(3),
                                               r=np.array([0.0, 0.0, 0.0]).reshape(3, 1),
                                               poses=deepcopy(triply_transformed_poses))

    for t_pose, dt_pose in zip(transformed_poses, doubly_transformed_poses):
        print("before scaling: {}".format(t_pose.pos_vec))
        print("after scaling: {}".format(dt_pose.pos_vec))

    return quadruply_transformed_poses


def main():
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    plot_func = plot_camera_positions

    real_poses = extract_robot_camera_poses(load_robot_poses(
        path_to_poses_dir="/mnt/storage/shared/roboweldar/new_dataset/new_dataset_reconstruction"))

    computed_poses = extract_inferred_camera_poses(load_computed_poses(
        path_to_cameras_sfm="/mnt/storage/roboweldar/simulation_test_1/MeshroomCache/StructureFromMotion/578f830addc4cce0c6fccaca48fd23068ffff1a3/cameras.sfm"))

    transformed_poses = pipeline(real_poses, computed_poses)

    # plot_func(ax, [Pose(None, computed_gc, None)], 'y')
    # plot_func(ax, [Pose(None, real_gc, None)], 'y')
    # plot_func(ax, translate_poses(computed_poses, computed_gc), 'g')
    # plot_func(ax, translate_poses(real_poses, real_gc), 'r')

    plot_func(ax, real_poses, 'r')
    plot_func(ax, computed_poses, 'g')
    plot_func(ax, transformed_poses, 'b')
    plot_func(ax, center_poses(real_poses)[0], 'm')

    plt.show()


if __name__ == '__main__':
    main()