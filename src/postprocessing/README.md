# roboweldar-3d-reconstruction / Coordinate Transform


`transform_poses.py` is a script which transforms the reconstructed model produced
by AliceVision Meshroom into the world frame, for use in the path planning for welding.

## Getting Started

For installing basic requirements, see the main [README.md](../../README.md). :

### Running the script

To run the standalone script, from `transform_poses.py` import 
`transform_model_to_world_coordinates()`, which takes the following arguments:

- **path_to_poses_dir**: the path to the directory which contains the raw images and `.npy` camera pose files. 
- **path_to_cameras_sfm**:  the path to the directory which contains the `cameras.sfm` file, typically located in the `cache/*/StructureFromMotion` directory.
- **path_to_computed_mesh**: the path to the directory which contains the `.obj`, `.png` and `.mtl` files, typically located in the `cache/*/Texturing` directory.  
- **path_to_transformed_mesh_dir**: the path to the directory where the script should output the transformed mesh files (WARNING: directory should exist).
- **show_plot**: (Optional) If true, the real camera positions and computed positions, as well as the original and transformed meshes are visualized in a popup. 
- **exclude_poses**: (Optional) A list of strings containing the filenames (without extensions) of the images corresponding to the camera positions that you would like to exclude from the computation.  
 

### Implementation details

The script uses the known camera
positions provided by the robot, in the world frame, to perform a series
of linear transformation (traslation, rotation, scaling) in order to bring the 
model from the arbitrary frame into the world frame. 

The following trasnformations are used:

under construction


## Authors

* **Orfeas Kypris** - *Initial work* - [orphefs](https://github.com/orphefs)

See also the list of [contributors](https://github.com/orgs/ikh-innovation/teams/roboweldar) who participated in this project.

## License

~~This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details~~

## Acknowledgments

* Props to the AliceVision Meshroom development community
* Props to my cats for being cool

