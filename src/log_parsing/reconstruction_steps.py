import inspect
import sys
from typing import List, Tuple

from src.log_parsing.log_parser import ReconstructionStep


# This module contains only reconstruction steps

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


def collect_steps() -> List[Tuple[str, type]]:
    return inspect.getmembers(sys.modules[__name__], inspect.isclass)


