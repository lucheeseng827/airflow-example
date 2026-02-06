"""
Backup Automation Example

Automates database and file backups:
- Backup databases
- Backup file systems
- Compress and encrypt backups
- Upload to cloud storage
- Verify backups
- Cleanup old backups
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "devops-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["devops@example.com"],
    "email_on_failure": True,
    "retries": 3,
    "retry_delay": timedelta(minutes=10),
    "sla": timedelta(hours=2),
}

dag = DAG(
    "backup_automation",
    default_args=default_args,
    description="Automated backup pipeline",
    schedule_interval="0 2 * * *",  # Daily at 2 AM
    catchup=False,
    tags=["devops", "backup", "automation"],
)


def backup_database(**context):
    """Backup database to file."""
    execution_date = context["ds_nodash"]
    backup_file = f"/backups/db_backup_{execution_date}.sql"

    print(f"Backing up database to {backup_file}")
    # Simulated: pg_dump or mysqldump
    print("✓ Database backup completed")

    return backup_file


def compress_backup(**context):
    """Compress backup file."""
    ti = context["task_instance"]
    backup_file = ti.xcom_pull(task_ids="backup_database")

    compressed_file = f"{backup_file}.gz"
    print(f"Compressing {backup_file} to {compressed_file}")
    print("✓ Compression completed")

    return compressed_file


def upload_to_s3(**context):
    """Upload backup to S3."""
    ti = context["task_instance"]
    compressed_file = ti.xcom_pull(task_ids="compress_backup")
    execution_date = context["ds"]

    s3_path = f"s3://backups/databases/{execution_date}/"
    print(f"Uploading {compressed_file} to {s3_path}")
    # Simulated: boto3 S3 upload
    print("✓ Upload to S3 completed")

    return s3_path


def verify_backup(**context):
    """Verify backup integrity."""
    ti = context["task_instance"]
    s3_path = ti.xcom_pull(task_ids="upload_to_s3")

    print(f"Verifying backup at {s3_path}")
    # Simulated: checksum verification
    print("✓ Backup verification successful")


def cleanup_old_backups():
    """Remove backups older than 30 days."""
    retention_days = 30
    print(f"Cleaning up backups older than {retention_days} days")
    # Simulated: delete old files
    print("✓ Cleanup completed - 5 old backups removed")


# Backup tasks
backup_db = PythonOperator(
    task_id="backup_database",
    python_callable=backup_database,
    provide_context=True,
    dag=dag,
)

backup_files = BashOperator(
    task_id="backup_files",
    bash_command='echo "Backing up /var/www... ✓ File backup completed"',
    dag=dag,
)

# Compress
compress = PythonOperator(
    task_id="compress_backup",
    python_callable=compress_backup,
    provide_context=True,
    dag=dag,
)

# Encrypt
encrypt = BashOperator(
    task_id="encrypt_backup",
    bash_command='echo "Encrypting backup... ✓ Encryption completed"',
    dag=dag,
)

# Upload
upload = PythonOperator(
    task_id="upload_to_s3",
    python_callable=upload_to_s3,
    provide_context=True,
    dag=dag,
)

# Verify
verify = PythonOperator(
    task_id="verify_backup",
    python_callable=verify_backup,
    provide_context=True,
    dag=dag,
)

# Cleanup
cleanup = PythonOperator(
    task_id="cleanup_old_backups",
    python_callable=cleanup_old_backups,
    dag=dag,
)

# Send notification
notify = BashOperator(
    task_id="send_notification",
    bash_command='echo "📧 Backup completed successfully"',
    dag=dag,
)

# Workflow
[backup_db, backup_files] >> compress >> encrypt >> upload >> verify
verify >> [cleanup, notify]
