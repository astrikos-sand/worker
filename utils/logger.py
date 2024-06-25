import logging


def setup_logger():
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Set the log level for the logger
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()

    # Set log levels for handlers
    console_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
