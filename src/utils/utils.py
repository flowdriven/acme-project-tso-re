from pathlib import Path
from datetime import datetime
import os
import logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
DB_DIR = PROJECT_ROOT / "db"

prefix = os.getenv("PREFIX", "acme-tso-re")
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_path = str(LOGS_DIR / f"{prefix}_{timestamp}.log")

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("xml_processing")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_paths(dataset: str):
    XML_PATH = PROJECT_ROOT / "data" / f"{dataset}.xml"
    XSD_PATH = PROJECT_ROOT / "schemas" / f"{dataset}.xsd"

    return {
        "xml_path": XML_PATH,
        "xsd_path": XSD_PATH,
        "db_path": DB_DIR
    }
