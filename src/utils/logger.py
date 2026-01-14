import logging
from pathlib import Path


def setup_logger(
    log_name: str = "logfile",
    level: int = logging.INFO,
    folder: str | Path = ".",
):

    logger = logging.getLogger("oil_simulation")

    if logger.handlers:
        return logger

    logger.setLevel(level)

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(folder / f"{log_name}.log", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
