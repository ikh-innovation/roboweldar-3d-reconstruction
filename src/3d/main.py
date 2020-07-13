import subprocess
import os
import glob

from config import ROOT_DIR


def main():
    path_to_images = os.path.join(ROOT_DIR, "test", "box_reconstruction", "raw")
    path_to_output = os.path.join(ROOT_DIR, "test", "box_reconstruction", "output")
    path_to_meshroom_bin = os.path.join(ROOT_DIR, "deps", "Meshroom-2019.2.0", "meshroom_photogrammetry")

    assert os.path.isdir(path_to_output)
    assert os.path.isdir(path_to_images)
    assert os.path.isfile(path_to_meshroom_bin)

    # images = glob.glob(os.path.join(path_to_images, "*.JPG"))

    myenv = os.environ.copy()
    myenv[
        'PATH'] = "/mnt/storage/roboweldar/Meshroom-2019.2.0/aliceVision/bin"  # visible in this process + all children
    myenv[
        'LD_LIBRARY_PATH'] = "/mnt/storage/roboweldar/Meshroom-2019.2.0/aliceVision/lib"  # visible in this process + all children

    try:
        subprocess.check_call([path_to_meshroom_bin,
                               "--input", path_to_images,
                               "--output", path_to_output,
                               "--forceStatus"],
                              env=myenv)
    except OSError:
        subprocess.check_call(["kill $(ps aux | grep '[m]eshroom' | awk '{print $2}'"])


if __name__ == '__main__':
    main()
