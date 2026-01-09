"""
SLA Monitoring Example

Demonstrates how to implement SLA monitoring:
- Set task-level SLAs
- Set DAG-level SLAs
- Custom SLA miss callbacks
- Performance tracking
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """
    Custom callback when SLA is missed.

    Args:
        dag: The DAG object
        task_list: List of tasks that missed SLA
        blocking_task_list: List of tasks blocking SLA tasks
        slas: List of SlaMiss objects
        blocking_tis: Task instances that are blocking
    """
    print("🚨 SLA MISS DETECTED!")
    print("=" * 60)

    for sla in slas:
        print(f"Task ID: {sla.task_id}")
        print(f"DAG ID: {sla.dag_id}")
        print(f"Execution Date: {sla.execution_date}")
        print(f"Expected Duration: {sla.sla}")
        print(f"Timestamp: {sla.timestamp}")
        print("-" * 60)

        # In production, send alerts here
        # send_pagerduty_alert(sla)
        # send_slack_alert(sla)
        # send_email_alert(sla)

    print(f"Total SLA misses: {len(slas)}")
    print("=" * 60)


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["sla-alerts@example.com"],
    "email_on_failure": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "sla": timedelta(hours=2),  # Default SLA for all tasks
}

dag = DAG(
    "sla_monitoring_example",
    default_args=default_args,
    description="Monitor task SLAs and alert on violations",
    schedule_interval="@hourly",
    catchup=False,
    tags=["monitoring", "sla", "alerts"],
    sla_miss_callback=sla_miss_callback,
)


def critical_task():
    """Simulated critical task - must complete quickly."""
    import time

    print("Running critical task...")
    time.sleep(2)  # Simulated work
    print("✓ Critical task completed")


def normal_task():
    """Simulated normal priority task."""
    import time

    print("Running normal task...")
    time.sleep(5)  # Simulated work
    print("✓ Normal task completed")


def long_running_task():
    """Simulated long-running task."""
    import time

    print("Running long task...")
    time.sleep(10)  # Simulated work
    print("✓ Long task completed")


# Critical task with strict SLA (5 minutes)
critical = PythonOperator(
    task_id="critical_data_processing",
    python_callable=critical_task,
    sla=timedelta(minutes=5),
    dag=dag,
)

# Normal priority task with moderate SLA (30 minutes)
normal = PythonOperator(
    task_id="normal_processing",
    python_callable=normal_task,
    sla=timedelta(minutes=30),
    dag=dag,
)

# Long-running task with relaxed SLA (2 hours)
long_running = PythonOperator(
    task_id="long_running_processing",
    python_callable=long_running_task,
    sla=timedelta(hours=2),
    dag=dag,
)

# Task without specific SLA (inherits DAG default)
reporting = BashOperator(
    task_id="generate_report",
    bash_command='echo "Generating report..." && sleep 3 && echo "✓ Report generated"',
    dag=dag,
)

# Workflow
critical >> normal >> long_running >> reporting
