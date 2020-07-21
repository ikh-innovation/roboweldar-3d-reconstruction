import importlib
import logging

from src.log_parsing.log_parser import ReconstructionStep
from src.log_parsing.reconstruction_steps import collect_steps
from src.log_parsing import reconstruction_steps

module = importlib.import_module(reconstruction_steps.__name__)

# create logger with 'spam_application'
logger = logging.getLogger('3D-reconstruction-scheduler')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('3D-reconstruction-scheduler.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def batch_parse_logs():
    for name, step_type in collect_steps():
        _class = getattr(module, name)
        if _class.__bases__[0] == ReconstructionStep:
            obj = _class("/home/orfeas/Documents/Code/roboweldar/roboweldar-3d-reconstruction/test/box_reconstruction/cache")
            print(obj)


if __name__ == '__main__':
    batch_parse_logs()
