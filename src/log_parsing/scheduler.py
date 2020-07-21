import importlib

from src.log_parsing.reconstruction_steps import collect_steps
from src.log_parsing import reconstruction_steps

module = importlib.import_module(reconstruction_steps.__name__)


def batch_parse_logs():
    for name, step_type in collect_steps():
        print(name)
        print(step_type)
        _class = getattr(module, name)
        obj = _class("/home/orfeas/Documents/Code/roboweldar/roboweldar-3d-reconstruction/test/box_reconstruction/cache")
        print(obj.__class__.__name__)
        print(obj.datetime_start)
        print(obj.datetime_end)
        print(obj.datetime_elapsed)
        print(obj)

if __name__ == '__main__':
    batch_parse_logs()
