# Airflow Best Practices

Production-ready patterns for building reliable, maintainable pipelines.

## DAG Design Principles

### 1. Keep DAGs Simple and Focused

**Do**: One DAG per business process
```python
# Good: Focused on single purpose
dag_customer_etl = DAG('customer_etl', ...)
dag_product_etl = DAG('product_etl', ...)

# Bad: Too many responsibilities
dag_everything = DAG('all_etl_jobs', ...)  # Don't do this
```

**Do**: Break complex workflows into multiple DAGs
```python
# Instead of one massive DAG:
dag_preprocessing = DAG('data_preprocessing', ...)
dag_training = DAG('model_training', ...)  # Triggered by preprocessing
dag_deployment = DAG('model_deployment', ...)  # Triggered by training
```

### 2. Use Static start_date

**Always use a fixed datetime:**
```python
# Good
'start_date': datetime(2024, 1, 1)

# Bad - creates inconsistent behavior
'start_date': datetime.now()
'start_date': datetime.today()
```

### 3. Idempotency is Critical

Tasks should produce the same result when run multiple times.

**Good: Idempotent patterns**
```python
# Overwrite file
def save_data():
    df.to_csv('/data/output.csv', mode='w')

# Delete and insert
def load_database():
    execute("DELETE FROM table WHERE date = '{{ ds }}'")
    execute("INSERT INTO table VALUES (...)")

# Upsert (update or insert)
def upsert_records():
    execute("""
        INSERT INTO table (id, data)
        VALUES (1, 'new')
        ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data
    """)
```

**Bad: Non-idempotent patterns**
```python
# Appends every run - data duplicates!
def bad_save():
    df.to_csv('/data/output.csv', mode='a')

# Inserts without checking existence
def bad_load():
    execute("INSERT INTO table VALUES (...)")  # Duplicates!
```

### 4. Avoid Top-Level Code in DAG Files

DAG files are parsed frequently by the scheduler. Keep them lightweight.

**Good:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def my_task():
    # Heavy imports only when task runs
    import pandas as pd
    import heavy_ml_library

    # Expensive operations only at task runtime
    data = fetch_large_dataset()
    result = expensive_computation(data)

dag = DAG('efficient_dag', ...)

task = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag,
)
```

**Bad:**
```python
from airflow import DAG
# Bad: Heavy import at parse time
import heavy_ml_library

# Bad: Expensive operation at parse time
data = fetch_large_dataset()  # Runs every time scheduler parses!
config = expensive_computation()  # Don't do this

dag = DAG('inefficient_dag', ...)
```

### 5. Use Connection and Variable Management

**Store credentials securely:**
```python
from airflow.hooks.base import BaseHook
from airflow.models import Variable

def my_task():
    # Get connection from Airflow connections
    conn = BaseHook.get_connection('my_database')
    db_url = f"postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"

    # Get variables from Airflow variables
    api_key = Variable.get("api_key")
    bucket_name = Variable.get("s3_bucket")

# Don't hardcode credentials!
# db_url = "postgresql://user:pass@host/db"  # Never do this
```

## Task Design

### 1. Granular Tasks

**Good: Small, focused tasks**
```python
extract = PythonOperator(task_id='extract', ...)
transform = PythonOperator(task_id='transform', ...)
validate = PythonOperator(task_id='validate', ...)
load = PythonOperator(task_id='load', ...)

extract >> transform >> validate >> load
```

**Benefits:**
- Easier debugging
- Better retry granularity
- Clearer monitoring
- Parallel execution opportunities

**Bad: Monolithic tasks**
```python
# Don't put everything in one task
do_everything = PythonOperator(task_id='etl', ...)  # Too big!
```

### 2. Use Appropriate Operators

**Choose the right tool:**
```python
# For bash commands
BashOperator(bash_command='echo "hello"')

# For Python functions
PythonOperator(python_callable=my_function)

# For SQL queries
PostgresOperator(sql='SELECT * FROM table')

# For HTTP requests
HttpOperator(endpoint='/api/data')

# For waiting
TimeDeltaSensor(delta=timedelta(hours=1))
```

### 3. Implement Proper Error Handling

```python
def robust_task(**context):
    """Task with comprehensive error handling."""
    try:
        # Attempt operation
        result = risky_operation()

        # Validate result
        if not validate_result(result):
            raise ValueError("Invalid result")

        return result

    except SpecificException as e:
        # Handle known errors
        logger.error(f"Known error occurred: {e}")
        # Maybe send notification
        send_alert(f"Task failed with known error: {e}")
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        # Send critical alert
        send_critical_alert(f"Unexpected failure: {e}")
        raise

    finally:
        # Cleanup resources
        cleanup_resources()

task = PythonOperator(
    task_id='robust_task',
    python_callable=robust_task,
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=30),
)
```

### 4. Use XCom for Small Data Only

**Good: Small metadata**
```python
def task1(**context):
    record_count = process_data()
    # Store small value
    context['task_instance'].xcom_push(key='record_count', value=record_count)

def task2(**context):
    # Retrieve value
    count = context['task_instance'].xcom_pull(task_ids='task1', key='record_count')
```

**Bad: Large data**
```python
# Don't do this - use external storage instead
def bad_task(**context):
    huge_dataframe = pd.read_csv('large_file.csv')  # 1GB
    context['task_instance'].xcom_push(key='data', value=huge_dataframe)  # Bad!

# Good: Use S3, GCS, or database
def good_task(**context):
    huge_dataframe = pd.read_csv('large_file.csv')
    s3_path = save_to_s3(huge_dataframe)
    context['task_instance'].xcom_push(key='s3_path', value=s3_path)  # Good!
```

## Configuration Management

### 1. Environment-Based Configuration

```python
import os
from airflow import DAG

# Detect environment
ENV = os.getenv('AIRFLOW_ENV', 'dev')

# Environment-specific config
CONFIG = {
    'dev': {
        'db_conn_id': 'dev_db',
        's3_bucket': 'dev-bucket',
        'retries': 0,
    },
    'staging': {
        'db_conn_id': 'staging_db',
        's3_bucket': 'staging-bucket',
        'retries': 1,
    },
    'prod': {
        'db_conn_id': 'prod_db',
        's3_bucket': 'prod-bucket',
        'retries': 3,
    }
}

dag = DAG(
    'env_aware_dag',
    default_args={
        'retries': CONFIG[ENV]['retries'],
    },
    ...
)
```

### 2. Use DAG-Level Configuration

```python
# config.py
DAG_CONFIGS = {
    'customer_etl': {
        'schedule': '@daily',
        'retries': 3,
        'sla': timedelta(hours=2),
        'owner': 'data-team',
    },
    'product_etl': {
        'schedule': '@hourly',
        'retries': 2,
        'sla': timedelta(minutes=30),
        'owner': 'product-team',
    }
}

# dag.py
from config import DAG_CONFIGS

config = DAG_CONFIGS['customer_etl']

dag = DAG(
    'customer_etl',
    schedule_interval=config['schedule'],
    default_args={
        'retries': config['retries'],
        'sla': config['sla'],
        'owner': config['owner'],
    }
)
```

## Dependency Management

### 1. Clear Dependency Chains

```python
# Good: Clear linear flow
extract >> transform >> load

# Good: Clear parallel branches
extract >> [transform_customers, transform_orders] >> join >> load

# Good: Complex but readable
start >> preprocessing
preprocessing >> [feature_eng_1, feature_eng_2, feature_eng_3]
[feature_eng_1, feature_eng_2] >> join_features
[join_features, feature_eng_3] >> model_training
model_training >> [evaluate, deploy]
evaluate >> notify
```

### 2. Use TriggerDagRunOperator for Cross-DAG Dependencies

```python
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Trigger dependent DAG
trigger = TriggerDagRunOperator(
    task_id='trigger_next_pipeline',
    trigger_dag_id='downstream_dag',
    wait_for_completion=True,
    poke_interval=60,
    dag=dag,
)

last_task >> trigger
```

## Testing

### 1. Unit Test Your Python Functions

```python
# tasks/etl.py
def transform_data(data):
    """Transform data (pure function)."""
    return [x * 2 for x in data]

# test/test_etl.py
import unittest
from tasks.etl import transform_data

class TestETL(unittest.TestCase):
    def test_transform_data(self):
        input_data = [1, 2, 3]
        expected = [2, 4, 6]
        result = transform_data(input_data)
        self.assertEqual(result, expected)
```

### 2. Validate DAG Structure

```python
# test/test_dags.py
from airflow.models import DagBag
import unittest

class TestDAGIntegrity(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)

    def test_no_import_errors(self):
        """Ensure all DAGs load without errors."""
        self.assertEqual(len(self.dagbag.import_errors), 0,
                        f"Import errors: {self.dagbag.import_errors}")

    def test_dag_count(self):
        """Ensure expected number of DAGs."""
        self.assertGreaterEqual(len(self.dagbag.dags), 1)

    def test_required_tags(self):
        """Ensure DAGs have required tags."""
        for dag_id, dag in self.dagbag.dags.items():
            self.assertTrue(len(dag.tags) > 0,
                          f"DAG {dag_id} missing tags")

    def test_retries_configured(self):
        """Ensure all tasks have retries."""
        for dag_id, dag in self.dagbag.dags.items():
            for task in dag.tasks:
                self.assertIsNotNone(task.retries,
                                   f"Task {task.task_id} missing retries")
```

### 3. Integration Testing

```python
# Run specific task for testing
def test_task_execution():
    """Test actual task execution."""
    from airflow.models import DagBag
    from datetime import datetime

    dagbag = DagBag(dag_folder='dags/')
    dag = dagbag.get_dag('my_dag')
    task = dag.get_task('my_task')

    # Test run
    task.run(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 1),
        ignore_first_depends_on_past=True,
        ignore_ti_state=True,
    )
```

## Performance Optimization

### 1. Parallelize When Possible

```python
# Process multiple datasets in parallel
extract_task >> [
    process_dataset_1,
    process_dataset_2,
    process_dataset_3,
] >> combine_results
```

### 2. Use Pools for Resource Management

```python
# Limit concurrent access to database
task = PostgresOperator(
    task_id='db_query',
    sql='SELECT * FROM large_table',
    pool='database_pool',  # Max 5 concurrent
    dag=dag,
)
```

### 3. Batch Processing

```python
def process_in_batches():
    """Process large dataset in batches."""
    batch_size = 1000

    for i in range(0, total_records, batch_size):
        batch = fetch_records(offset=i, limit=batch_size)
        process_batch(batch)
        save_batch(batch)
```

## Monitoring & Alerting

### 1. Implement Comprehensive Callbacks

```python
default_args = {
    'on_failure_callback': alert_on_failure,
    'on_success_callback': log_success,
    'on_retry_callback': log_retry,
    'sla': timedelta(hours=2),
}
```

### 2. Use Tags for Organization

```python
dag = DAG(
    'customer_pipeline',
    tags=['customer', 'etl', 'daily', 'critical'],
    ...
)
```

### 3. Set Appropriate SLAs

```python
# Critical tasks
critical_task = PythonOperator(
    task_id='critical_process',
    sla=timedelta(minutes=30),
    ...
)

# Less critical tasks
report_task = PythonOperator(
    task_id='generate_report',
    sla=timedelta(hours=4),
    ...
)
```

## Security Best Practices

### 1. Never Hardcode Credentials

```python
# Bad
DATABASE_URL = "postgresql://user:password@host/db"

# Good
from airflow.hooks.base import BaseHook
conn = BaseHook.get_connection('my_db')
```

### 2. Use Secrets Backend

```python
# airflow.cfg
[secrets]
backend = airflow.providers.hashicorp.secrets.vault.VaultBackend
backend_kwargs = {"url": "http://vault:8200", "token": "your-token"}
```

### 3. Limit DAG Permissions

```python
dag = DAG(
    'sensitive_pipeline',
    access_control={
        'Admin': {'can_read', 'can_edit'},
        'DataTeam': {'can_read'},
    }
)
```

## Documentation

### 1. Document Your DAGs

```python
dag = DAG(
    'customer_etl',
    description='Extract customer data from API, transform, and load to warehouse',
    doc_md="""
    # Customer ETL Pipeline

    ## Purpose
    Synchronize customer data from CRM to data warehouse.

    ## Schedule
    Runs daily at 2 AM UTC

    ## Dependencies
    - Requires CRM API access
    - Writes to Redshift warehouse

    ## Alerts
    - Slack: #data-alerts
    - Email: data-team@example.com

    ## Runbook
    See: https://wiki.example.com/customer-etl
    """,
    ...
)
```

### 2. Document Tasks

```python
task = PythonOperator(
    task_id='extract_customers',
    doc_md="""
    ### Extract Customers
    Fetches customer records from CRM API.

    **API Endpoint**: /api/v1/customers
    **Rate Limit**: 100 req/min
    **Expected Records**: ~10,000/day
    """,
    ...
)
```

## Summary Checklist

- [ ] Static start_date
- [ ] Idempotent tasks
- [ ] Minimal top-level code
- [ ] Secure credential management
- [ ] Appropriate retries and SLAs
- [ ] Comprehensive error handling
- [ ] Unit and integration tests
- [ ] Clear task dependencies
- [ ] Proper documentation
- [ ] Monitoring and alerting
- [ ] Environment-based configuration
- [ ] Resource pools for limiting concurrency
- [ ] Tags for organization
- [ ] XCom only for small data

## Resources

- [Official Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Astronomer Best Practices](https://docs.astronomer.io/learn/category/best-practices)
- [Testing Guide](testing-guide.md)
- [Monitoring Guide](monitoring-guide.md)
