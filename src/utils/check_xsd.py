from lxml import etree
from typing import Tuple, List


def validate_xsd(xml_string: str, xsd_string: str) -> Tuple[bool, List[str]]:
    """
    Validate XML string content against an XSD string.

    Args:
        xml_string (str): XML document as a string.
        xsd_string (str): XSD schema as a string.

    Returns:
        Tuple[bool, List[str]]: 
            - True if XML is valid, False otherwise.
            - List of validation error messages.
    """
    try:
        schema_root = etree.XML(xsd_string.encode())
        schema = etree.XMLSchema(schema_root)

        xml_doc = etree.fromstring(xml_string.encode())

        is_valid = schema.validate(xml_doc)
        error_messages = []

        if not is_valid:
            for error in schema.error_log:
                error_messages.append(f"Line {error.line}, Col {error.column}: {error.message}")

        return is_valid, error_messages

    except (etree.XMLSyntaxError, etree.XMLSchemaParseError) as e:
        return False, [f"Parsing error: {str(e)}"]

    except Exception as e:
        return False, [f"Unexpected error: {str(e)}"]