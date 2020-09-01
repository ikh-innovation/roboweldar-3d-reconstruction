from src.pose_input.extract_poses import load_robot_poses, load_computed_poses
import matplotlib.pyplot as plt
import numpy as np

def plot_robot_camera_poses(real_poses):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    position_vectors = []
    rotation_matrices = []
    for id, rm in real_poses.items():
        rot_mat = rm[:3, :3]
        print(rm)
        pos_vec = rm[:3, 3]
        rotation_matrices.append(rot_mat)
        position_vectors.append(pos_vec)
        plt.quiver(pos_vec[0], pos_vec[1], pos_vec[2], rot_mat[:, 0], rot_mat[:, 1], rot_mat[:, 2], length=0.1,
                   normalize=True)
    plt.axis("auto")
    plt.show()


def plot_inferred_camera_poses(computed_poses):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    position_vectors = []
    rotation_matrices = []
    for id, data in computed_poses.items():
        rot_mat = np.array(data["rotation"])
        print(rm)
        pos_vec = rm[:3, 3]
        rotation_matrices.append(rot_mat)
        position_vectors.append(pos_vec)
        plt.quiver(pos_vec[0], pos_vec[1], pos_vec[2], rot_mat[:, 0], rot_mat[:, 1], rot_mat[:, 2], length=0.1,
                   normalize=True)
    plt.axis("auto")
    plt.show()


def main():
    real_poses = load_robot_poses(
        path_to_poses_dir="/mnt/storage/shared/roboweldar/new_dataset/new_dataset_reconstruction")
    plot_robot_camera_poses(real_poses)

    computed_poses = load_computed_poses(
        path_to_cameras_sfm="/mnt/storage/roboweldar/simulation_test_1/MeshroomCache/StructureFromMotion/578f830addc4cce0c6fccaca48fd23068ffff1a3/cameras.sfm")
    plot_inferred_camera_poses(computed_poses)

    plt.show()


if __name__ == '__main__':
    main()
