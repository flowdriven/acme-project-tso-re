import os

from utils.utils import setup_logger, get_paths
from utils.check_xsd import validate_xsd
from utils.check_xml import process_xml

dataset_list = os.getenv("DATASET_LIST", "provisional,final").split(",")
prefix = os.getenv("PREFIX")

def read_file_as_string(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    
def main():
    logger = setup_logger()

    for dataset in dataset_list:
        paths = get_paths(dataset) 

        xml_string = read_file_as_string(paths["xml_path"])
        xsd_string = read_file_as_string(paths["xsd_path"])

        # xsd schema validation 
        is_valid, errors = validate_xsd(xml_string, xsd_string)

        if is_valid:
            logger.info("✅ XML is valid against the XSD.")
        else:
            logger.error("❌ XML is invalid. Errors:")
            for err in errors:
                logger.error(f"  - {err}")

        # quality checks  
        is_valid, errors = process_xml(xml_string)

        if is_valid:
            logger.info("✅ XML is valid.")
        else:
            logger.error("❌ XML is invalid. Errors:")
            for err in errors:
                logger.error(f"{errors}")

    # write db 

if __name__ == '__main__':
    main()