import logging


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
