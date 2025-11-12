import argparse
import os
from typing import Any


def extend_dict(dict_to_extend: dict[str, Any], key: str):
    if key not in dict_to_extend.keys():
        dict_to_extend[key] = {}


def validate_file_path(path: str):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist.")
    return path


def validate_folder_path(path: str):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Folder '{path}' does not exist.")
    return path
