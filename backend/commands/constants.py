import sys

IMPULSE_DIR_PATH = '/Users/csmith/Desktop/projects/impulse'

def initialize_command():
    if IMPULSE_DIR_PATH not in sys.path:
        sys.path.append(IMPULSE_DIR_PATH)

    return