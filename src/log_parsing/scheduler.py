import importlib
import logging

from config import LOGGING_ENABLED
from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.reconstruction_steps import collect_steps
from src.log_parsing import reconstruction_steps
from src.noop_logger import NoopLogger

module = importlib.import_module(reconstruction_steps.__name__)

if LOGGING_ENABLED:
    logger = logging.getLogger("3d-reconstruction-service.scheduler")
else:
    logger = NoopLogger


def batch_parse_logs(path_to_cache_dir: str) -> list:
    list_of_reconstruction_steps = []
    for name, step_type in collect_steps():
        _reconstruction_step_class = getattr(module, name)
        # check if parent class is ReconstructionStep
        if _reconstruction_step_class.__bases__[0] == ReconstructionStep:
            rec_step_obj = _reconstruction_step_class(path_to_cache_dir)
            print("Debug directory: {}".format(path_to_cache_dir))
            list_of_reconstruction_steps.append(rec_step_obj)
            if logger:
                logger.info("Parsed reconstruction step: {}".format(rec_step_obj))
    return list_of_reconstruction_steps
