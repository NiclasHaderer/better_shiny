import functools
import logging
import time
from typing import Callable, Any


def create_logger(name: str) -> logging.Logger:
    # Check if uvicorn is installed
    try:
        from uvicorn import logging as uvicorn_logging

        formatter = uvicorn_logging.DefaultFormatter("%(levelprefix)s %(message)s")
    except ImportError:
        logging_format = "%(levelname)-9s %(message)s"
        formatter = logging.Formatter(logging_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def log_duration(
        function: Callable[..., Any],
        thing: str | None = None,
        logger: logging.Logger | None = None,
) -> Callable[..., Any]:
    if logger is None:
        logger = create_logger(function.__module__)

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        duration = time.time() - start_time
        if duration > 0.1:
            logger.warning(f"{thing if thing else function.__name__} took {duration:.3f} seconds.")
        else:
            logger.info(f"{thing if thing else function.__name__} took {duration:.3f} seconds.")
        return result

    return wrapper
