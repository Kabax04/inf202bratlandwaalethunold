import logging
from pathlib import Path


def setup_logger(
    log_name: str = "logfile",
    level: int = logging.INFO,
    folder: str | Path = ".",
):
    """
    Configure and return a logger that writes messages to a file.

    Creates a file handler that logs to <folder>/<log_name>.log with timestamps,
    log levels, and message names. If logger already exists, returns it without
    reconfiguring (prevents duplicate handlers).

    Args:
        log_name (str, optional): Name of the log file (without .log extension).
                                  Default: "logfile"
        level (int, optional): Logging level (e.g., logging.INFO, logging.DEBUG).
                               Default: logging.INFO
        folder (str | Path, optional): Directory where log file will be saved.
                                       Created if it doesn't exist.
                                       Default: "." (current directory)

    Returns:
        logging.Logger: Configured logger instance named "oil_simulation".
                        Ready to use for logging messages.

    Example:
        logger = setup_logger("simulation", level=logging.DEBUG, folder="results")
        logger.info("Simulation started")
    """
    # Get or create logger with fixed name "oil_simulation"
    logger = logging.getLogger("oil_simulation")

    # Prevent duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    # Set the logging level threshold
    logger.setLevel(level)

    # Ensure output folder exists
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    # Create file handler that writes to <folder>/<log_name>.log (overwrites existing file)
    file_handler = logging.FileHandler(folder / f"{log_name}.log", mode="w")

    # Define log message format: timestamp - level - logger_name - message
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Attach handler to logger
    logger.addHandler(file_handler)

    # Prevent messages from propagating to parent loggers (avoid duplicate logs)
    logger.propagate = False

    return logger
