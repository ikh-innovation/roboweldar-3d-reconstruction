from pathlib import Path
import os

import open3d as o3d


def simplify_mesh_decimate(path_to_transformed_mesh: str, path_to_output_mesh: str):
    mesh = o3d.io.read_triangle_mesh(path_to_transformed_mesh)
    simplified_mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=20000)

    o3d.io.write_triangle_mesh(path_to_output_mesh,
                               simplified_mesh, print_progress=True)


def simplify_mesh_clustering(path_to_transformed_mesh: str, path_to_output_mesh: str):
    mesh = o3d.io.read_triangle_mesh(path_to_transformed_mesh)
    voxel_size = max(mesh.get_max_bound() - mesh.get_min_bound()) / 64
    print(f'voxel_size = {voxel_size:e}')
    simplified_mesh = mesh.simplify_vertex_clustering(
        voxel_size=voxel_size,
        contraction=o3d.geometry.SimplificationContraction.Average)

    o3d.io.write_triangle_mesh(path_to_output_mesh,
                               simplified_mesh, print_progress=True)


if __name__ == '__main__':
    simplify_mesh_clustering(
        "/home/orfeas/Documents/Code/roboweldar/roboweldar-3d-reconstruction/src/rest/roboweldar_networking/server/uploads/mesh/transformed_mesh.obj",
        "/tmp/simplified_mesh.obj")
