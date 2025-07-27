from lxml import etree
from datetime import datetime
import os 
import pytz

datetime_tags = os.getenv("DATETIME_TAGS", "FromTimestamp,ToTimestamp,CreationTimestamp").split(",")
indexed_id = os.getenv("INDEXED_ID", "MeterPointId")
date_from, date_to = os.getenv("RANGE", "FromTimestamp,ToTimestamp").split(",")
reading_list = os.getenv("READING_LIST")

errors = []

def check_one_full_day(xml_root) -> tuple[bool, str]:
    """
    Checks that the time period in the XML is exactly 1 day.
    """ 
    try:
        from_elem = xml_root.find(f".//{date_from}")
        to_elem = xml_root.find(f".//{date_to}")

        if from_elem is None or to_elem is None:
            return False, f"Missing {date_from} or {date_to}."

        if not from_elem.text or not to_elem.text:
            return False, f"{date_from} or {date_to} is empty."

        from_dt = datetime.fromisoformat(from_elem.text)
        to_dt = datetime.fromisoformat(to_elem.text)

        delta = to_dt - from_dt
        if delta.total_seconds() == 86400:  # 24h = 86400s
            return True, ""
        else:
            return False, f"Period is not exactly 1 day: {delta}."

    except Exception as e:
        return False, f"Error checking period duration: {str(e)}"

def validate_two_decimals(xml_root) -> tuple[bool, list]:
    """
    Validates that all <Value> elements inside <ReadingList> have exactly 2 decimal places.
    Returns (True, []) if all are valid, or (False, [error messages]) otherwise.
    """
    reading_values = xml_root.findall(".//ReadingList/Reading/Value")
    #reading_values = xml_root.findall(".//{reading_list}")

    for i, value_elem in enumerate(reading_values, start=1):
        if value_elem is None or not value_elem.text:
            errors.append(f"Reading {i}: missing or empty <Value>.")
            continue

        try:
            value_str = value_elem.text.strip()
            if "." not in value_str:
                errors.append(f"Reading {i}: value '{value_str}' has no decimal part.")
                continue

            decimal_part = value_str.split(".")[1]
            if len(decimal_part) != 2:
                errors.append(f"Reading {i}: value '{value_str}' does not have exactly 2 decimal places.")
        except Exception as e:
            errors.append(f"Reading {i}: error validating value '{value_elem.text}': {str(e)}")

    return (len(errors) == 0), errors

def validate_sequence_numbers(xml_root) -> tuple[bool, list]:
    """
    Checks that <Sequence> values in <ReadingList> start from 1 and increment by 1 with no gaps or duplicates.
    Returns (True, []) if valid, or (False, [error messages]) if not.
    """
    try:
        sequence_elements = xml_root.findall(".//ReadingList/Reading/Sequence")

        if not sequence_elements:
            return False, ["No <Sequence> elements found."]

        try:
            sequence_numbers = [int(seq.text.strip()) for seq in sequence_elements]
        except Exception as e:
            return False, [f"Failed to parse one or more <Sequence> elements as integers: {str(e)}"]

        expected = list(range(1, len(sequence_numbers) + 1))

        if sequence_numbers != expected:
            errors.append(f"Invalid sequence order. Expected {expected}, got {sequence_numbers}.")

        return (len(errors) == 0), errors

    except Exception as e:
        return False, [f"Error validating sequence numbers: {str(e)}"]

def process_xml(xml_string: str) -> tuple[bool, dict]:
    """
    Process XML string content and run quality checks.

    Args:
        xml_string (str): XML document as a string.

    Returns:
        Tuple[bool, List[str]]: 
            - True if XML is valid, False otherwise.
            - Dictionary with: 
                - Indexed id value 
                - Formatted xml
                - List of validation error messages
    """

    try:

        try: 
            root = etree.fromstring(xml_string.encode("utf-8"))
        except Exception as e:
            return False, {"Errors": [f"XML parsing failed: {str(e)}"]}

        # Validate 1-day duration
        full_day_ok, full_day_msg = check_one_full_day(root)
        if not full_day_ok:
            errors.append(full_day_msg)

        # Validate that values must contain exactly 2 decimals
        decimal_ok, decimal_errors = validate_two_decimals(root)
        if not decimal_ok:
            errors.append(decimal_errors)

        # Validate that the sequence numbers must start 
        # from 1 and go incrementally with no gaps.
        is_sequence_valid, sequence_errors = validate_sequence_numbers(root)
        if not is_sequence_valid:
            errors.append(sequence_errors)

        # Get the ID required for indexing the table 
        indexed_id_elem = root.find(f".//{indexed_id}")
        if indexed_id_elem is None or not indexed_id_elem.text:
            errors.append("Missing or empty indexed id element.")
            indexed_id_value = None
        else:
            indexed_id_value = indexed_id_elem.text

        for tag in datetime_tags:
            elem = root.find(f".//{tag}")
            if elem is None:
                errors.append(f"Missing {tag} element.")
            elif not elem.text:
                errors.append(f"{tag} is empty.")
            else:
                # Convert to datetime object (with timezone)
                dt_local = datetime.fromisoformat(elem.text)
                # Convert to UTC
                dt_utc = dt_local.astimezone(pytz.UTC)
                # Replace with UTC ISO string
                elem.text = dt_utc.isoformat()

        converted_xml_str = etree.tostring(root, encoding="unicode")

        return (len(errors) == 0), {
            "IndexedId": indexed_id_value,
            "ConvertedXml": converted_xml_str,
            "Errors": errors
        }

    except Exception as e:
        return False, {"Errors": [f"Unexpected error: {str(e)}"]}