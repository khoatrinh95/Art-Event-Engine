import logging
from pathlib import Path
from typing import Union
from datetime import datetime


from .config import LOG_FILE, VERBOSE_LOGGING

LOGGER_NAME = "event_engine"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)
logger.propagate = False


def setup_logger(log_file: Union[Path, str] = LOG_FILE, verbose: bool = VERBOSE_LOGGING):
    """Configure event engine logging to a file."""
    if logger.handlers:
        return logger

    handler = logging.FileHandler(Path(log_file), encoding="utf-8")
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-5s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    logger.info("Logging initialized. verbose=%s", verbose)
    return logger



class LoggerEventEngine:
    """Singleton logger for the event engine."""
    _instance = None

    def __new__(cls, log_file: Union[Path, str] = LOG_FILE, verbose: bool = VERBOSE_LOGGING):
        if cls._instance is None:
            cls._instance = super(LoggerEventEngine, cls).__new__(cls)
            cls._instance.logger = setup_logger(log_file=log_file, verbose=verbose)
        return cls._instance

    @classmethod
    def get_logger(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self, location: str):
        self.logger.info("Art Event Engine started for %s", location)
        self.logger.info("Run started at %s", datetime.now().strftime('%Y-%m-%d %H:%M'))

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def header(self, message: str, *args, **kwargs):
        self.logger.info("%s", "=" * 60)
        self.logger.info("  %s", message % args if args else message, **kwargs)
        self.logger.info("%s", "=" * 60)

    