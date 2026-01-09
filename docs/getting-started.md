# Getting Started with Apache Airflow

## What is Apache Airflow?

Apache Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It allows you to define your workflows as code (Python), making them maintainable, versionable, testable, and collaborative.

## Core Concepts

### 1. DAG (Directed Acyclic Graph)

A DAG is a collection of tasks with directional dependencies. It defines:
- What tasks to run
- When to run them
- In what order
- How to handle failures

**Key Properties:**
- **Directed**: Tasks have a clear flow direction (A → B → C)
- **Acyclic**: No circular dependencies (prevents infinite loops)
- **Graph**: Visual representation of task relationships

### 2. Tasks

Tasks are the building blocks of a DAG. Each task represents a single unit of work:
- Running a Python function
- Executing a bash command
- Querying a database
- Calling an API
- Transferring data

### 3. Operators

Operators determine what each task actually does. Common operators:

- **BashOperator**: Execute bash commands
- **PythonOperator**: Run Python functions
- **EmailOperator**: Send emails
- **HttpOperator**: Make HTTP requests
- **SqlOperator**: Execute SQL queries
- **Sensor**: Wait for a condition to be met

### 4. Schedule Interval

Defines how often a DAG should run:
- Cron expressions: `0 0 * * *` (daily at midnight)
- Timedelta: `timedelta(hours=1)` (every hour)
- Presets: `@daily`, `@hourly`, `@weekly`
- Manual: `None` (trigger manually)

### 5. Execution Date

The logical date/time for which the DAG run is scheduled (NOT when it actually runs).

## Your First DAG

Here's a simple example to understand the structure:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'hello_world',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define tasks
def print_hello():
    print('Hello from Python!')
    return 'success'

task1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

task2 = PythonOperator(
    task_id='say_hello',
    python_callable=print_hello,
    dag=dag,
)

task3 = BashOperator(
    task_id='print_goodbye',
    bash_command='echo "Goodbye!"',
    dag=dag,
)

# Set dependencies
task1 >> task2 >> task3  # task1 runs first, then task2, then task3
```

## Understanding Default Arguments

Default arguments apply to all tasks in the DAG:

```python
default_args = {
    'owner': 'airflow',              # Owner of the DAG
    'depends_on_past': False,         # Don't depend on previous runs
    'start_date': datetime(2024, 1, 1),  # When the DAG starts
    'email': ['admin@example.com'],   # Email for notifications
    'email_on_failure': True,         # Email on task failure
    'email_on_retry': False,          # Don't email on retry
    'retries': 1,                     # Retry failed tasks once
    'retry_delay': timedelta(minutes=5),  # Wait 5 min before retry
}
```

## Task Dependencies

Multiple ways to define task relationships:

```python
# Method 1: Bitshift operators (recommended)
task1 >> task2 >> task3  # Linear: 1 → 2 → 3

# Method 2: Fan-out
task1 >> [task2, task3]  # Parallel: 1 → 2
                          #          1 → 3

# Method 3: Fan-in
[task1, task2] >> task3  # Join: 1 → 3
                          #       2 → 3

# Method 4: Complex
task1 >> [task2, task3] >> task4  # Diamond pattern

# Method 5: Set methods
task1.set_downstream(task2)
task2.set_upstream(task1)
```

## Airflow Architecture

```
┌─────────────────┐
│   Web Server    │  ← UI for monitoring and managing DAGs
└────────┬────────┘
         │
┌────────▼────────┐
│   Scheduler     │  ← Triggers DAG runs and submits tasks
└────────┬────────┘
         │
┌────────▼────────┐
│    Executor     │  ← Determines how tasks are executed
└────────┬────────┘
         │
┌────────▼────────┐
│    Workers      │  ← Actually run the tasks
└────────┬────────┘
         │
┌────────▼────────┐
│    Metadata DB  │  ← Stores DAG, task, and run state
└─────────────────┘
```

## Best Practices for Beginners

### 1. Idempotency
Tasks should produce the same result when run multiple times:

```python
# Bad: Appends to file each run
def bad_task():
    with open('data.txt', 'a') as f:
        f.write('new data\n')

# Good: Overwrites file each run
def good_task():
    with open('data.txt', 'w') as f:
        f.write('new data\n')
```

### 2. Use Latest Operators

```python
# Old (deprecated)
from airflow.operators.bash_operator import BashOperator

# New (current)
from airflow.operators.bash import BashOperator
```

### 3. Set Catchup Carefully

```python
# Catchup=True: Runs all missed DAG runs since start_date
# Catchup=False: Only runs for current period
dag = DAG(
    'my_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,  # Don't backfill
)
```

### 4. Use Templating

Airflow supports Jinja templating for dynamic values:

```python
task = BashOperator(
    task_id='templated_task',
    bash_command='echo "Execution date: {{ ds }}"',  # ds = YYYY-MM-DD
    dag=dag,
)
```

Common template variables:
- `{{ ds }}`: Execution date (YYYY-MM-DD)
- `{{ ds_nodash }}`: Execution date (YYYYMMDD)
- `{{ execution_date }}`: Full datetime object
- `{{ params.my_param }}`: Custom parameters

### 5. Test Your DAGs

```bash
# Test DAG syntax
python dags/my_dag.py

# List tasks
airflow tasks list my_dag

# Test a specific task
airflow tasks test my_dag task_id 2024-01-01
```

## Common Pitfalls to Avoid

1. **Don't use dynamic start_date**: Always use static datetime
   ```python
   # Bad
   'start_date': datetime.now()

   # Good
   'start_date': datetime(2024, 1, 1)
   ```

2. **Don't perform heavy computation in DAG file**: Only define structure
   ```python
   # Bad: Runs every time scheduler parses DAGs
   data = expensive_api_call()

   # Good: Runs only when task executes
   def my_task():
       data = expensive_api_call()
   ```

3. **Don't use top-level code**: Keep DAG file lightweight
   ```python
   # Bad
   import heavy_library
   result = process_data()

   # Good
   def my_task():
       import heavy_library
       result = process_data()
   ```

## Next Steps

1. Explore [Operators Guide](operators-guide.md)
2. Review [Basic Examples](../dags/01_basics/)
3. Learn about [Testing](testing-guide.md)
4. Study [Best Practices](best-practices.md)

## Useful Commands

```bash
# Initialize database
airflow db init

# Create admin user
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# Start webserver
airflow webserver --port 8080

# Start scheduler
airflow scheduler

# List DAGs
airflow dags list

# Trigger a DAG
airflow dags trigger my_dag

# Pause/unpause a DAG
airflow dags pause my_dag
airflow dags unpause my_dag

# Test a task
airflow tasks test my_dag my_task 2024-01-01

# View task logs
airflow tasks logs my_dag my_task 2024-01-01
```

## Troubleshooting

### DAG not showing up in UI?
- Check for Python syntax errors
- Ensure DAG file is in the `dags/` folder
- Wait for scheduler to parse (default: every 5 minutes)
- Check scheduler logs

### Tasks not running?
- Ensure scheduler is running
- Check task state in UI
- Review task logs for errors
- Verify dependencies are met

### Import errors?
- Check if all required packages are installed
- Verify Python path includes your modules
- Review Airflow logs for import errors

## Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Astronomer Learn](https://docs.astronomer.io/learn)
- [Airflow GitHub](https://github.com/apache/airflow)
