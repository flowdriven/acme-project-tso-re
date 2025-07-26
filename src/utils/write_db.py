from pathlib import Path
from datetime import datetime
import sqlite3
import os 

db_dir, db_name = os.getenv("DB_DIR", "db,acme_tso_re.db").split(",")

# Path to the SQLite database file at project root
DB_PATH = Path(__file__).resolve().parent.parent.parent / db_dir / db_name


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xml_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL,
                content TEXT NOT NULL,
                source_system TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_record_id ON xml_data(record_id)")
        conn.commit()

#def store_xml_record(record_id: str, xml_string: str, source_system: str):
def store_xml_record(payload: dict):
    """
    Inserts a new record into the xml_data table.

    Args:
        record_id (str): ID extracted from the XML.
        xml_string (str): Raw XML content.
        source_system (str): System that produced the XML.
    """
    record_id = payload["IndexedId"]
    xml_string = payload["ConvertedXml"]
    source_system = payload["SourceSystem"]
    created_at = datetime.utcnow().timestamp()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO xml_data (record_id, content, source_system, created_at)
            VALUES (?, ?, ?, ?)
        """, (record_id, xml_string, source_system, created_at))
        conn.commit()