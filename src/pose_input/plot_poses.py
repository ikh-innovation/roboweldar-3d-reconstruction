import copy
from copy import deepcopy
from functools import partial
from typing import List, Optional

from scipy.optimize import minimize

from src.pose_input.extract_poses import load_robot_poses, load_computed_poses
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d


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


def plot_camera_positions_matplotlib(ax, poses, color, marker):
    for pose in poses:
        ax.scatter(pose.pos_vec[0], pose.pos_vec[1], pose.pos_vec[2], color=color, marker=marker, alpha=0.6)
    plt.axis("auto")


def plot_camera_positions_open3d(ax, poses, color):
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

    # print(compute_geometric_center(ordered_real_poses))
    # print(compute_geometric_center(ordered_computed_poses))

    r_reals = [pose.pos_vec for pose in ordered_real_poses]
    r_computeds = [pose.pos_vec for pose in ordered_computed_poses]

    partial_func_optimal_rotation = partial(optimal_rotation, r_reals, r_computeds)
    res2 = minimize(partial_func_optimal_rotation, x0_Omega, method='Nelder-Mead', tol=1e-12)
    alpha = res2.x[0]
    beta = res2.x[1]
    gamma = res2.x[2]
    Omega = get_3d_rotation_matrix(alpha, beta, gamma)
    # print(alpha, beta, gamma)

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


def transform_poses(poses, scaling: Optional[np.ndarray] = None,
                    rotation: Optional[np.ndarray] = None,
                    translation: Optional[np.ndarray] = None):
    transformed_poses = deepcopy(poses)

    if translation is not None:
        for pose in transformed_poses:
            pose.pos_vec = pose.pos_vec + translation

    if rotation is not None:
        for pose in transformed_poses:
            pose.pos_vec = rotation @ pose.pos_vec

    if scaling is not None:
        for pose in transformed_poses:
            pose.pos_vec = scaling @ pose.pos_vec

    return transformed_poses


def compute_centroid(vertices: np.ndarray):
    xs = np.mean(vertices[:, 0])
    ys = np.mean(vertices[:, 1])
    zs = np.mean(vertices[:, 2])
    return np.array([xs, ys, zs]).reshape(3, 1)


def compute_geometric_center(poses: List[Pose]):
    vertices = np.zeros([len(poses), 3])
    for index, pose in enumerate(poses):
        vertices[index, :] = np.transpose(pose.pos_vec)
    centroid = compute_centroid(vertices)
    return centroid


def translate_poses(computed_poses, r_estimated):
    c = deepcopy(computed_poses)
    for pose in c:
        pose.pos_vec -= r_estimated

    return c


def check_omega(Omega: np.ndarray):
    # check if determinant of matrix = 1.0 (rotation matrix should satisfy this condition)
    return np.round(np.linalg.det(Omega), 2) == 1.0


def center_poses(poses):
    centroid = compute_geometric_center(poses)
    centered_poses = translate_poses(poses, centroid)
    return centered_poses, centroid


class Transformation:
    def __init__(self, translation: np.array, rotation: np.array, scaling: np.array):
        # order of transformation should be
        self.translation = translation
        self.rotation = rotation
        self.check_rotation()
        self.scaling = scaling

    def check_rotation(self):
        if not check_omega(self.rotation):
            raise UserWarning("Determinant of matrix is not 1.0, not a valid rotation matrix...")


def pipeline(real_poses, computed_poses):
    _, real_centroid = center_poses(real_poses)
    _, computed_centroid = center_poses(computed_poses)

    centered_real_poses = transform_poses(poses=real_poses, translation=-real_centroid)
    poses = transform_poses(poses=computed_poses, translation=-computed_centroid)
    print("Centroid of Centered computed poses: {}".format(center_poses(centered_real_poses)[1]))
    print("Centroid of Centered real poses: {}".format(center_poses(poses)[1]))

    # find optimal orientation
    rotation = optimize_rotation(centered_real_poses, poses)
    poses = transform_poses(poses=poses, rotation=rotation)

    # find optimal scaling
    scaling = optimize_scaling(centered_real_poses, poses)
    poses = transform_poses(poses=poses, scaling=scaling)

    # translate to centroid of real camera positions
    poses = transform_poses(poses=poses, translation=real_centroid)

    # for t_pose, dt_pose in zip(rotated_poses, doubly_transformed_poses):
    #     print("before scaling: {}".format(t_pose.pos_vec))
    #     print("after scaling: {}".format(dt_pose.pos_vec))
    # TODO: add some sanity checks

    return poses, Transformation(translation=real_centroid, rotation=rotation, scaling=scaling)


def transform_mesh(mesh: o3d.open3d_pybind.geometry.TriangleMesh,
                   transformation: Transformation) -> o3d.open3d_pybind.geometry.TriangleMesh:



    mesh_centroid = compute_centroid(np.asarray(mesh.vertices))
    # print("Center: {}".format(mesh_centered.get_center()))
    mesh_centered = copy.deepcopy(mesh).translate(mesh_centroid)
    mesh_rotated = mesh_centered.rotate(transformation.rotation, center=(0, 0, 0))
    mesh_scaled = mesh_rotated.scale(np.mean(np.diag(transformation.scaling)), center=mesh_rotated.get_center())
    print(transformation.scaling)
    mesh_translated = copy.deepcopy(mesh_scaled).translate(transformation.translation)

    return mesh_translated


def main():
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    plot_func = plot_camera_positions_matplotlib

    real_poses = extract_robot_camera_poses(load_robot_poses(
        path_to_poses_dir="/mnt/storage/roboweldar/3d_photogrammetry_test_5_real/raw"))

    computed_poses = extract_inferred_camera_poses(load_computed_poses(
        path_to_cameras_sfm="/mnt/storage/roboweldar/3d_photogrammetry_test_5_real/MeshroomCache/StructureFromMotion/b64967ba4da27d19d4bb573920fe598d32d57533/cameras.sfm"))

    transformed_poses, transformation = pipeline(real_poses, computed_poses)

    mesh = o3d.io.read_triangle_mesh(
        "/mnt/storage/roboweldar/3d_photogrammetry_test_5_real/MeshroomCache/Texturing/2313595eedec8610209d2540979821dd23fb181b/texturedMesh.obj")

    transformed_mesh = transform_mesh(mesh, transformation)

    coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame()
    o3d.visualization.draw_geometries([coord_frame, mesh, transformed_mesh])

    plot_func(ax, real_poses, color='r', marker="o")
    plot_func(ax, computed_poses, color='g', marker="o")
    plot_func(ax, transformed_poses, color='b', marker="*")
    plt.show()


if __name__ == '__main__':
    main()
