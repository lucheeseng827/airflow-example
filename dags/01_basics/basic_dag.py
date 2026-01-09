"""
Basic DAG Example

This is a simple introduction to Airflow DAGs showing fundamental concepts:
- DAG definition
- Task creation with operators
- Task dependencies
- Using templated fields
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments applied to all tasks
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "basic_example",
    default_args=default_args,
    description="A simple tutorial DAG",
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=["tutorial", "basics"],
)


# Python function to be executed
def print_context(**context):
    """Print execution context information."""
    print(f"Execution date: {context['execution_date']}")
    print(f"DAG run ID: {context['run_id']}")
    print(f"Task ID: {context['task'].task_id}")
    return "Task completed successfully!"


# Task 1: Print current date using bash
print_date = BashOperator(
    task_id="print_date",
    bash_command="date",
    dag=dag,
)

# Task 2: Sleep for 5 seconds
sleep = BashOperator(
    task_id="sleep",
    bash_command="sleep 5",
    dag=dag,
)

# Task 3: Execute Python function
run_python = PythonOperator(
    task_id="run_python",
    python_callable=print_context,
    provide_context=True,
    dag=dag,
)

# Task 4: Use templated command
templated = BashOperator(
    task_id="templated",
    bash_command='echo "Execution date: {{ ds }}"',
    dag=dag,
)

# Define task dependencies
# Linear flow: print_date -> sleep -> run_python -> templated
print_date >> sleep >> run_python >> templated
