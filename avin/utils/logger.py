# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from avin.utils import Date
from avin.utils.conf import cfg

__all__ = ("log", "configure_log")

LOGGER_NAME = "avin-logger"

log = logging.getLogger(LOGGER_NAME)


def configure_log(debug: bool, info: bool) -> logging.Logger:
    """
    Configure application logger (idempotent).
    Safe to call multiple times.
    """

    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    _add_stream_handler(logger)

    log_dir: Path = cfg.log_path
    log_dir.mkdir(parents=True, exist_ok=True)

    if info:
        _add_file_handler(
            logger,
            log_dir / f"{Date.today()}.log",
            level=logging.INFO,
            mode="a",
        )

    if debug:
        _add_file_handler(
            logger,
            log_dir / "debug.log",
            level=logging.DEBUG,
            mode="w",
        )

    return logger


def _add_stream_handler(logger: logging.Logger) -> None:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    logger.addHandler(handler)


def _add_file_handler(
    logger: logging.Logger,
    file_path: Path,
    level: int,
    mode: str,
) -> None:
    formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = RotatingFileHandler(
        file_path,
        maxBytes=10_000_000,
        backupCount=cfg.log_history_days,
        mode=mode,
        encoding="utf-8",
    )

    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
