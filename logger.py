# logger.py
import logging
from config import config

def setup_logger():
    logger = logging.getLogger("FileOrganizer")
    logger.setLevel(config.get("log_level", "INFO"))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler("file_organizer.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()