# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import logging
import os
from datetime import date as Date
from pathlib import Path

from avin.utils.conf import CFG

__all__ = ("log", "configure_log")

NAME = "avin-logger"
LOG_DIR = CFG.Dir.log
HISTORY = CFG.Log.history
DEBUG = CFG.Log.debug
INFO = CFG.Log.info

log = logging.getLogger(NAME)


def configure_log(debug: bool, info: bool):
    logger = logging.getLogger(NAME)
    __config_stream_log(logger)

    if info:
        info_log_path = os.path.join(LOG_DIR, f"{Date.today()}.log")
        __config_info_log(logger, info_log_path)

    if debug:
        debug_log_path = os.path.join(LOG_DIR, "debug.log")
        __config_debug_log(logger, debug_log_path)

    __delete_old_log_files(LOG_DIR, HISTORY)


def __config_stream_log(logger):
    stream_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)


def __config_debug_log(logger, file_path):
    file_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(file_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def __config_info_log(logger, file_path):
    file_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(file_path, mode="a")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def __delete_old_log_files(log_dir: Path, max_files: int) -> None:
    contents = os.listdir(log_dir)
    contents = [os.path.join(log_dir, i) for i in contents]

    files = [i for i in contents if os.path.isfile(i)]
    log_files = sorted([i for i in files if i.endswith(".log")])

    while len(log_files) > max_files:
        os.remove(log_files[0])  # remove oldest file in sorted file list
        log_files.pop(0)


if __name__ == "__main__":
    ...
else:
    configure_log(debug=DEBUG, info=INFO)
