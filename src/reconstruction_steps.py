from src.log_parser import ReconstructionStep


class CameraInit(ReconstructionStep):
    pass


class DepthMapFilter(ReconstructionStep):
    pass


class FeatureMatching(ReconstructionStep):
    pass


class MeshFiltering(ReconstructionStep):
    pass


class PrepareDenseScene(ReconstructionStep):
    pass


class StructureFromMotion(ReconstructionStep):
    pass


class DepthMap(ReconstructionStep):
    pass


class FeatureExtraction(ReconstructionStep):
    pass


class ImageMatching(ReconstructionStep):
    pass


class Meshing(ReconstructionStep):
    pass


class Publish(ReconstructionStep):
    pass


class Texturing(ReconstructionStep):
    pass


if __name__ == '__main__':
    #TODO: make log parsing automatic for all folders on regular intervals, to send POST requests to context broker
    ci = CameraInit(
        path_to_cache_dir="/home/orfeas/Documents/Code/roboweldar/roboweldar-3d-reconstruction/test/box_reconstruction/cache")
    print(ci.__class__.__name__)
    print(ci.datetime_start)
    print(ci.datetime_end)
    print(ci.datetime_elapsed)
