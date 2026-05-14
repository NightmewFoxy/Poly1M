"""Logger that writes to both stdout (Railway captures it) and a rotating file on the mounted volume."""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from config import LOG_FILE


def get_logger(name: str = "poly1m") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s :: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    try:
        rot = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
        rot.setFormatter(fmt)
        logger.addHandler(rot)
    except Exception as exc:  # disk not writable in some environments; stdout still works
        logger.warning("File logging disabled: %s", exc)

    logger.propagate = False
    return logger
