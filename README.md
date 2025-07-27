# XML Message Processor for Energy Trading

## 1. Scenario and Purpose

Acme's _(*)_ data engineering team is in charge of establishing integrations with external partners and developing data pipelines that support energy trading and sales systems and processes.

As part of a new contract, the Transmission System Operator (TSO) R.E. has provided two sample messages in XML format, representing two message types: “Provisional” and “Final.” Provisional data is delivered daily and refers to D-1 values, while Final data is provided monthly with M-1 granularity. It is essential to ensure that the most accurate and up-to-date data is available for downstream processes. Once the contract is active, the system is expected to handle approximately 5,000 XML messages per day.

This project implements a scalable and modular pipeline for reading, validating, and storing the XML messages, ensuring that the best available data is accessible in downstream systems. 

Functional Requirements: 

* The code must validate incoming files against predefined checks. If any validation fails, the corresponding data must be excluded from database storage. Validations: 
    * The file must contain data for exactly one full calendar day. 
    * All numeric values must be represented with exactly two decimal places.
    * Sequence numbers must begin at 1 and increment consecutively without any gaps.

* Datetime fields are required to be stored in UTC.

_(*) The company name used in this use case is fictitious and is intended solely for illustrative purposes._ 

## 2. Architecture overview

* **Ingestion layer**
    * XML messages from external providers

* **Processing layer**
    * Validation of message structure and content
    * Extraction of key fields (e.g., record_id)
    * Logging and error handling

* **Consumption layer**
    * Processed XML messages are stored into a db and availbale for query  

## 3. Code Structure

### Database Schema Approach 

* Store each message as a text field in the database, along with metadata to support indexing, querying, and traceability.  
    * Primary Key auto incremented
    * Arbitrary record identifier required for indexing the table
    * Raw XML message as text, for reprocessing
    * Source system as origin of the message (e.g., TSO name)
    * Timestamp when the message was stored
    * Message type, if provisional or final 

### Separation of Concerns

* The entry point of the application is `main.py`, which:  
    * Manages orchestration logic
    * Delegates business logic to modular, callable components
    * Handles logging to support error tracking and diagnostics
* Custom modules are responsible for:  
    * `check_xsd.py` xml schema validation against xsd
    * `check_xml.py` xml content validation and formatting 
    * `utils.py` set-up logger and project paths
    * `write_db.py` handler for storing to db

## 4. Tools

* **a) Python (Data Extract & Load)**
    * Version `3.12.8`
    * Custom-built modules (data validation and formatting)
    * `lxml` (XML processing)
    * `pytz` (timezone calculations)
    * Logging (error handling)
* **e) Other**
    * `.env` file (Configuration as Code)
    * `README.md` file (documentation)
    * `requirements.txt` (package management)

### Usage

```bash
cd .\src\
python .\main.py
```

## 6. Open Questions & Assumptions for Future Direction 

### Message Processing Strategy

#### Open Question:
Should messages be processed in real-time as they arrive, or in scheduled batches?

#### Suggested Approach:
Batch processing (e.g., hourly) is recommended to balance throughput and system load.
Real-time processing may be considered if latency requirements are strict.

### Pipeline Triggering Mechanism

#### Open Question:
How should the pipeline be triggered—event-driven or scheduled?

#### Suggested Approach:
If files are dropped in cloud storage (e.g., S3, Azure Blob), use event-driven triggers.
Otherwise, use scheduled DAGs (e.g., every hour in Airflow).

#### Best Practices:
Use Airflow sensors (e.g., S3KeySensor, FileSensor) for event-driven pipelines.
Combine with timeout and fallback logic to avoid stuck DAGs.

### File Retention and Lifecycle

#### Open Question:
Should processed files be deleted, archived, or retained?

#### Suggested Approach:
Move processed files to an archive folder.
Move invalid files to a quarantine folder.

#### Best Practices:
Apply a retention policy (e.g., 30–90 days) for both archive and quarantine.
Use timestamped (partitioned) folder structures for traceability (e.g., /archive/2025/07/27/).

### Handling Invalid Messages

#### Open Question:
Should invalid messages be retried or discarded?

#### Suggested Approach:
Store invalid messages in a quarantine table or storage with error metadata.
Enable manual or automated reprocessing.

#### Best Practices:
Log validation errors with clear error codes.
Use Airflow DAGs or CLI tools to reprocess quarantined data. 

## 8. Miscellaneous

### Database Schema

| Field name | Description | Field Type |
| --- | --- | --- |
| `id` | Primary Key | INT |
| `record_id` | Record identifier required for indexing | TEXT |
| `content` | Raw XML Message | TEXT |
| `source_sytem` | Origin of the message (e.g., TSO name) | TEXT |
| `created_at` | Time the message was stored | TIMESTAMP |
| `message_type` | Provisional or Final | TEXT |

### Project Structure

```bash
├── .env                               # Envinroment definition  
├── .gitignore
├── README.md
├── requirements.txt
├── data                               # Data samples
│   ├── final.xml
│   └── provisional.xml   
├── db                                 # db prototype
│   ├── acme_tso_re.db
├── logs                               # Logs for error handling
├── schemas                            # Data schemas
│   ├── final.xsd
│   └── provisional.xsd   
├── src
│   ├── __init__.py
│   ├── main.py                        # Entry point    
│   ├── utils
│   │   ├── __init__.py
│   │   ├── check_xml.py               # XML validation 
│   │   ├── check_xsd.py               # XSD schema validation 
│   │   ├── utils.py                   # Utilities (logger, project paths)  
│   │   └── write_db                   # Handler for db storing                         
```
