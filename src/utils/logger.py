import os
import logging

def get_logging(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # file handler
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler("logs/log.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

logger = get_logging(__name__)