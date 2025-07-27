import os

from utils.utils import setup_logger, get_paths
from utils.check_xsd import validate_xsd
from utils.check_xml import process_xml
from utils.write_db import init_db, store_xml_record

dataset_list = os.getenv("DATASET_LIST", "provisional,final").split(",")
prefix = os.getenv("PREFIX", "acme-tso-re")

def read_file_as_string(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    
def main():
    logger = setup_logger()

    for dataset in dataset_list:
        logger.info(f"Processing dataset: {dataset}")
        paths = get_paths(dataset) 
       
        try: 
            xml_string = read_file_as_string(paths["xml_path"])
            xsd_string = read_file_as_string(paths["xsd_path"])
        except FileNotFoundError as e:
            logger.error(str(e))
            continue

        # xsd schema validation 
        try: 
            is_valid_xsd, result_xsd = validate_xsd(xml_string, xsd_string)
        except Exception as e:
            logger.error(f"Exception during XSD validation: {e}")
            continue

        if is_valid_xsd:
            logger.info(f"XML {dataset} is valid against the XSD.")
        else:
            errors_xsd = result_xsd["Errors"]
            logger.error(f"! XML {dataset} is invalid. Errors:")
            logger.error(f"  - {errors_xsd}")
            result_xsd["Errors"].clear()

        # quality checks  
        try: 
            is_valid_xml, result_xml = process_xml(xml_string)
        except Exception as e:
            logger.error(f"Exception during XML processing: {e}")
            continue
        
        # store to db   
        if is_valid_xml:
            logger.info(f"XML {dataset} validation completed — status: VALID.")
            
            indexed_id = result_xml["IndexedId"]
            validated_xml = result_xml["ConvertedXml"]

            payload = {
                "IndexedId": indexed_id,
                "ConvertedXml": validated_xml, 
                "SourceSystem": prefix,
                "MessageType": dataset
            }

            success, errors = store_xml_record(payload) 
            if success:
                logger.info(f"XML {dataset} storing completed ")
            else:
                logger.error(f"! XML {dataset} storing failed. Errors:")
                logger.error(f"{errors}")
                errors.clear()
                
        else:
            errors_xml = result_xml["Errors"]
            logger.error(f"! XML {dataset} is invalid. Errors:")
            logger.error(f"{errors_xml}")
            result_xml["Errors"].clear()


if __name__ == '__main__':
    init_db()
    main()