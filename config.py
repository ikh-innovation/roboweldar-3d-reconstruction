import os

ROOT_DIR = os.path.split(os.path.abspath(__file__))[0]
MESHROOM_DIR = os.path.join(ROOT_DIR, "deps", "Meshroom-2019.2.0")
IMAGES_DIR = os.path.join(ROOT_DIR, "reconstruction_data", "raw")
OUTPUT_DIR = os.path.join(ROOT_DIR, "reconstruction_data", "output")
CACHE_DIR = os.path.join(ROOT_DIR, "reconstruction_data", "cache")



LOGGING_ENABLED = False