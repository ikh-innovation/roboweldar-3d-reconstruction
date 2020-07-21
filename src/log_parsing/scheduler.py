import importlib
import logging

from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.reconstruction_steps import collect_steps
from src.log_parsing import reconstruction_steps

module = importlib.import_module(reconstruction_steps.__name__)

logger = logging.getLogger("3d-reconstruction-service.scheduler")


def batch_parse_logs(path_to_cache_dir: str) -> list:
    list_of_reconstruction_steps = []
    for name, step_type in collect_steps():
        _reconstruction_step_class = getattr(module, name)
        # check if parent class is ReconstructionStep
        if _reconstruction_step_class.__bases__[0] == ReconstructionStep:
            rec_step_obj = _reconstruction_step_class(path_to_cache_dir)
            list_of_reconstruction_steps.append(rec_step_obj)
            logger.info("Parsed reconstruction step: {}".format(rec_step_obj))
    return list_of_reconstruction_steps


if __name__ == '__main__':
    batch_parse_logs(path_to_cache_dir="/home/orfeas/Documents/Code/roboweldar/" \
                                       "roboweldar-3d-reconstruction/test/box_reconstruction/cache")
