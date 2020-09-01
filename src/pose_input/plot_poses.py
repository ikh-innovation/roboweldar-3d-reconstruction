from src.pose_input.extract_poses import load_robot_poses
import matplotlib.pyplot as plt


def plot_vectors(augmented_rotation_matrices):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    position_vectors = []
    rotation_matrices = []
    for id, rm in augmented_rotation_matrices.items():
        rot_mat = rm[:3, :3]
        print(rm)
        pos_vec = rm[:3, 3]
        rotation_matrices.append(rot_mat)
        position_vectors.append(pos_vec)
        plt.quiver(pos_vec[0], pos_vec[1], pos_vec[2], rot_mat[:, 0], rot_mat[:, 1], rot_mat[:, 2], length=0.1,
                   normalize=True)
    plt.axis("auto")
    plt.show()




def main():
    augmented_rotation_matrices = load_robot_poses(
        path_to_poses_dir="/mnt/storage/shared/roboweldar/new_dataset/new_dataset_reconstruction")
    plot_vectors(augmented_rotation_matrices)


if __name__ == '__main__':
    main()
