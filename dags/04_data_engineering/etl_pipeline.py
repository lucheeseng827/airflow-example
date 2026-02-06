"""
ETL Pipeline Example

Typical data engineering workflow:
- Extract data from multiple sources (API, Database, Files)
- Transform and clean data
- Validate data quality
- Load to data warehouse
- Update metadata
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["data-team@example.com"],
    "email_on_failure": True,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "sla": timedelta(hours=4),
}

dag = DAG(
    "etl_pipeline",
    default_args=default_args,
    description="ETL pipeline from multiple sources to warehouse",
    schedule_interval="0 */6 * * *",  # Every 6 hours
    catchup=False,
    tags=["data-engineering", "etl", "warehouse"],
)


def extract_from_api(**context):
    """Extract data from REST API."""
    execution_date = context["ds"]

    print(f"Extracting data from API for {execution_date}")
    print("API endpoint: https://api.example.com/data")
    print("Fetching records...")

    # Simulated API call
    print("✓ Extracted 10,000 records from API")

    return {"source": "api", "records": 10000}


def extract_from_database(**context):
    """Extract data from source database."""
    execution_date = context["ds"]

    print(f"Extracting data from database for {execution_date}")
    print("Running query: SELECT * FROM users WHERE updated_at >= '{execution_date}'")

    # Simulated database query
    print("✓ Extracted 5,000 records from database")

    return {"source": "database", "records": 5000}


def extract_from_files(**context):
    """Extract data from CSV files."""
    execution_date = context["ds"]

    print(f"Extracting data from S3 for {execution_date}")
    print("S3 path: s3://data-lake/raw/2024-01-01/*.csv")

    # Simulated file reading
    print("✓ Extracted 2,000 records from files")

    return {"source": "files", "records": 2000}


def transform_data(**context):
    """Transform and clean data."""
    ti = context["task_instance"]

    # Get data from all extract tasks
    api_data = ti.xcom_pull(task_ids="extract_api")
    db_data = ti.xcom_pull(task_ids="extract_database")
    file_data = ti.xcom_pull(task_ids="extract_files")

    total_records = api_data["records"] + db_data["records"] + file_data["records"]

    print(f"Transforming {total_records} total records...")
    print("Applying transformations:")
    print("  - Removing duplicates")
    print("  - Standardizing formats")
    print("  - Handling missing values")
    print("  - Type conversions")
    print("  - Creating derived columns")

    cleaned_records = int(total_records * 0.95)  # Simulated cleaning
    print(f"✓ Transformation completed - {cleaned_records} clean records")

    return {
        "total_records": total_records,
        "cleaned_records": cleaned_records,
        "duplicates_removed": total_records - cleaned_records,
    }


def validate_data(**context):
    """Run data quality checks."""
    ti = context["task_instance"]
    transform_result = ti.xcom_pull(task_ids="transform_data")

    print("Running data quality checks...")

    # Simulated validation
    checks = {
        "schema_validation": True,
        "null_check": True,
        "range_check": True,
        "referential_integrity": True,
        "uniqueness_check": True,
    }

    print("Data Quality Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    if not all(checks.values()):
        raise ValueError("Data quality checks failed!")

    print(f"✓ All quality checks passed for {transform_result['cleaned_records']} records")


def load_to_warehouse(**context):
    """Load data to data warehouse."""
    ti = context["task_instance"]
    transform_result = ti.xcom_pull(task_ids="transform_data")
    execution_date = context["ds"]

    print(f"Loading {transform_result['cleaned_records']} records to warehouse...")
    print(f"Target table: warehouse.fact_events")
    print(f"Partition: date={execution_date}")

    # Simulated load
    print("Loading strategy: UPSERT")
    print("✓ Data loaded successfully")

    return {
        "table": "warehouse.fact_events",
        "records_loaded": transform_result["cleaned_records"],
        "partition": execution_date,
    }


def update_metadata(**context):
    """Update metadata catalog."""
    ti = context["task_instance"]
    load_result = ti.xcom_pull(task_ids="load_warehouse")

    print("Updating metadata catalog...")
    print(f"Table: {load_result['table']}")
    print(f"Records: {load_result['records_loaded']}")
    print(f"Partition: {load_result['partition']}")
    print("✓ Metadata updated")


def send_summary_report(**context):
    """Send summary report."""
    ti = context["task_instance"]

    transform_result = ti.xcom_pull(task_ids="transform_data")
    load_result = ti.xcom_pull(task_ids="load_warehouse")

    print("📊 ETL Pipeline Summary Report")
    print("=" * 50)
    print(f"Records extracted: {transform_result['total_records']}")
    print(f"Records cleaned: {transform_result['cleaned_records']}")
    print(f"Duplicates removed: {transform_result['duplicates_removed']}")
    print(f"Records loaded: {load_result['records_loaded']}")
    print(f"Target: {load_result['table']}")
    print("=" * 50)
    print("✓ Pipeline completed successfully")


# Define tasks
start = DummyOperator(task_id="start", dag=dag)

# Extract from multiple sources in parallel
extract_api = PythonOperator(
    task_id="extract_api",
    python_callable=extract_from_api,
    provide_context=True,
    dag=dag,
)

extract_db = PythonOperator(
    task_id="extract_database",
    python_callable=extract_from_database,
    provide_context=True,
    dag=dag,
)

extract_files = PythonOperator(
    task_id="extract_files",
    python_callable=extract_from_files,
    provide_context=True,
    dag=dag,
)

# Transform
transform = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

# Validate
validate = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)

# Load
load = PythonOperator(
    task_id="load_warehouse",
    python_callable=load_to_warehouse,
    provide_context=True,
    dag=dag,
)

# Update metadata
update_meta = PythonOperator(
    task_id="update_metadata",
    python_callable=update_metadata,
    provide_context=True,
    dag=dag,
)

# Send report
report = PythonOperator(
    task_id="send_report",
    python_callable=send_summary_report,
    provide_context=True,
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag)

# Workflow - Extract in parallel, then sequential transform/load
start >> [extract_api, extract_db, extract_files] >> transform
transform >> validate >> load >> update_meta >> report >> end
