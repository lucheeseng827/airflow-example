# Monitoring & Observability Guide

## Why Monitor Your Airflow Pipelines?

Effective monitoring helps you:
- **Detect failures early**: Catch issues before they impact downstream systems
- **Track performance**: Identify bottlenecks and optimize resource usage
- **Ensure SLAs**: Meet data freshness and availability requirements
- **Debug issues**: Quickly identify root causes of failures
- **Plan capacity**: Understand resource needs and scale appropriately

## Levels of Monitoring

### 1. DAG-Level Monitoring

Track the health and performance of entire workflows.

#### Key Metrics:
- **DAG Run Duration**: How long does the entire pipeline take?
- **Success Rate**: Percentage of successful runs
- **Schedule Delay**: Gap between scheduled time and actual start time
- **Active Runs**: Number of concurrent DAG executions

#### Implementation:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'sla': timedelta(hours=2),  # Alert if task takes > 2 hours
}

dag = DAG(
    'monitored_pipeline',
    default_args=default_args,
    description='Pipeline with monitoring',
    schedule_interval='@daily',
    max_active_runs=1,  # Prevent concurrent runs
    catchup=False,
)
```

### 2. Task-Level Monitoring

Monitor individual task execution.

#### Key Metrics:
- **Task Duration**: Execution time per task
- **Retry Count**: How often tasks fail and retry
- **Task State**: Success, failure, skipped, running
- **Resource Usage**: CPU, memory, disk I/O

#### Task Callbacks:

```python
def on_failure_callback(context):
    """Custom callback when task fails."""
    task_instance = context['task_instance']
    exception = context.get('exception')

    # Send custom alert
    send_slack_alert(
        channel='#data-alerts',
        message=f"Task {task_instance.task_id} failed: {exception}"
    )

    # Log to monitoring service
    log_to_datadog({
        'metric': 'airflow.task.failure',
        'tags': [
            f'dag:{task_instance.dag_id}',
            f'task:{task_instance.task_id}'
        ]
    })

def on_success_callback(context):
    """Custom callback when task succeeds."""
    task_instance = context['task_instance']
    duration = task_instance.duration

    # Track performance
    log_metric('task_duration', duration, tags={
        'dag': task_instance.dag_id,
        'task': task_instance.task_id
    })

def on_retry_callback(context):
    """Custom callback when task retries."""
    task_instance = context['task_instance']

    # Increment retry counter
    increment_counter('task.retries', tags={
        'dag': task_instance.dag_id,
        'task': task_instance.task_id
    })

task = PythonOperator(
    task_id='monitored_task',
    python_callable=my_function,
    on_failure_callback=on_failure_callback,
    on_success_callback=on_success_callback,
    on_retry_callback=on_retry_callback,
    dag=dag,
)
```

### 3. SLA Monitoring

Service Level Agreements ensure tasks complete within expected timeframes.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when SLA is missed."""
    for sla in slas:
        print(f"SLA missed for task: {sla.task_id}")
        # Send alert to PagerDuty
        trigger_pagerduty_alert({
            'severity': 'warning',
            'summary': f'SLA missed: {sla.task_id}',
            'details': {
                'dag_id': dag.dag_id,
                'execution_date': sla.execution_date,
                'expected_duration': sla.sla
            }
        })

dag = DAG(
    'sla_monitored_dag',
    default_args={
        'start_date': datetime(2024, 1, 1),
        'sla': timedelta(hours=1),  # Default SLA for all tasks
    },
    schedule_interval='@hourly',
    sla_miss_callback=sla_miss_callback,
)

# Task with custom SLA
critical_task = PythonOperator(
    task_id='critical_etl',
    python_callable=etl_function,
    sla=timedelta(minutes=30),  # This task must complete in 30 min
    dag=dag,
)
```

## Monitoring Strategies

### 1. Health Checks

Implement automated health checks for your pipelines.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

def check_data_freshness():
    """Verify data is fresh enough."""
    from datetime import datetime
    import pytz

    last_update = get_last_data_update_time()
    now = datetime.now(pytz.UTC)
    age = now - last_update

    max_age = timedelta(hours=2)
    if age > max_age:
        raise Exception(f"Data is stale: {age} old (max: {max_age})")

    print(f"Data is fresh: {age} old")

def check_data_quality():
    """Verify data quality metrics."""
    metrics = {
        'row_count': get_row_count(),
        'null_percentage': get_null_percentage(),
        'duplicate_percentage': get_duplicate_percentage(),
    }

    # Define thresholds
    if metrics['row_count'] < 1000:
        raise Exception(f"Row count too low: {metrics['row_count']}")

    if metrics['null_percentage'] > 5.0:
        raise Exception(f"Too many nulls: {metrics['null_percentage']}%")

    if metrics['duplicate_percentage'] > 1.0:
        raise Exception(f"Too many duplicates: {metrics['duplicate_percentage']}%")

    print(f"Data quality checks passed: {metrics}")

dag = DAG(
    'health_check_pipeline',
    default_args={'start_date': datetime(2024, 1, 1)},
    schedule_interval='@hourly',
)

freshness_check = PythonOperator(
    task_id='check_freshness',
    python_callable=check_data_freshness,
    dag=dag,
)

quality_check = PythonOperator(
    task_id='check_quality',
    python_callable=check_data_quality,
    dag=dag,
)

freshness_check >> quality_check
```

### 2. Custom Metrics

Send custom metrics to monitoring platforms.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import time

def track_processing_metrics(**context):
    """Track custom metrics during processing."""
    start_time = time.time()

    # Process data
    records_processed = process_data()

    # Calculate metrics
    duration = time.time() - start_time
    records_per_second = records_processed / duration

    # Send to monitoring service
    send_to_datadog([
        {
            'metric': 'pipeline.records.processed',
            'value': records_processed,
            'tags': ['dag:my_pipeline', 'env:production']
        },
        {
            'metric': 'pipeline.processing.duration',
            'value': duration,
            'tags': ['dag:my_pipeline', 'env:production']
        },
        {
            'metric': 'pipeline.records.per_second',
            'value': records_per_second,
            'tags': ['dag:my_pipeline', 'env:production']
        }
    ])

    # Store in XCom for downstream tasks
    context['task_instance'].xcom_push(
        key='records_processed',
        value=records_processed
    )

dag = DAG('metrics_pipeline', default_args={'start_date': datetime(2024, 1, 1)})

task = PythonOperator(
    task_id='process_with_metrics',
    python_callable=track_processing_metrics,
    provide_context=True,
    dag=dag,
)
```

### 3. Alerting Patterns

Different alert strategies for different scenarios.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Pattern 1: Immediate Critical Alerts
def critical_failure_callback(context):
    """Immediate alert for critical failures."""
    send_pagerduty_alert(
        severity='critical',
        summary='Critical pipeline failure',
        details=context
    )

    send_slack_alert(
        channel='#incidents',
        message=f"🚨 CRITICAL: {context['task_instance'].task_id} failed",
        mention='@oncall'
    )

# Pattern 2: Delayed Warnings
def warning_after_retries(context):
    """Alert only after multiple retries."""
    task_instance = context['task_instance']

    if task_instance.try_number >= 2:  # After 2nd retry
        send_slack_alert(
            channel='#warnings',
            message=f"⚠️ Task failing repeatedly: {task_instance.task_id}"
        )

# Pattern 3: Digest Alerts
def daily_digest_callback(context):
    """Aggregate failures for daily digest."""
    failures = get_failures_last_24h()

    if len(failures) > 0:
        send_email(
            to='team@example.com',
            subject='Daily Pipeline Digest',
            body=format_digest_email(failures)
        )

# Pattern 4: Smart Throttling
def throttled_alert(context):
    """Prevent alert fatigue with throttling."""
    task_id = context['task_instance'].task_id
    last_alert = get_last_alert_time(task_id)

    # Only alert once per hour
    if last_alert is None or (datetime.now() - last_alert) > timedelta(hours=1):
        send_alert(context)
        record_alert_time(task_id, datetime.now())
```

## Monitoring Tools Integration

### 1. Prometheus & Grafana

Export Airflow metrics to Prometheus:

```python
# Install: pip install apache-airflow-providers-prometheus

# airflow.cfg
[metrics]
statsd_on = True
statsd_host = localhost
statsd_port = 9125
statsd_prefix = airflow
```

Example Grafana dashboard queries:
```promql
# DAG run duration
histogram_quantile(0.95,
  rate(airflow_dagrun_duration_seconds_bucket[5m])
)

# Task failure rate
rate(airflow_task_failed_total[5m])

# Scheduler heartbeat
airflow_scheduler_heartbeat
```

### 2. Datadog

```python
from datadog import initialize, statsd

initialize(
    api_key='your_api_key',
    app_key='your_app_key'
)

def send_to_datadog(metrics):
    """Send metrics to Datadog."""
    for metric in metrics:
        statsd.gauge(
            metric['metric'],
            metric['value'],
            tags=metric.get('tags', [])
        )
```

### 3. CloudWatch (AWS)

```python
import boto3

def send_to_cloudwatch(namespace, metric_name, value, dimensions):
    """Send metrics to CloudWatch."""
    cloudwatch = boto3.client('cloudwatch')

    cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': 'Count',
                'Dimensions': dimensions
            }
        ]
    )

# Usage in task
def my_task():
    records = process_data()

    send_to_cloudwatch(
        namespace='Airflow/Pipelines',
        metric_name='RecordsProcessed',
        value=len(records),
        dimensions=[
            {'Name': 'DAG', 'Value': 'my_dag'},
            {'Name': 'Environment', 'Value': 'production'}
        ]
    )
```

## Logging Best Practices

### 1. Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

def structured_log(level, message, **kwargs):
    """Log with structured data."""
    log_data = {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    getattr(logger, level)(json.dumps(log_data))

def my_task(**context):
    structured_log('info',
        'Starting data processing',
        dag_id=context['dag'].dag_id,
        task_id=context['task'].task_id,
        execution_date=str(context['execution_date'])
    )

    records = process_data()

    structured_log('info',
        'Processing complete',
        records_processed=len(records),
        duration_seconds=123.45
    )
```

### 2. Context-Rich Logging

```python
def my_task(**context):
    """Task with rich logging context."""
    ti = context['task_instance']

    logger.info(f"Starting task: {ti.task_id}")
    logger.info(f"DAG: {ti.dag_id}")
    logger.info(f"Execution date: {context['execution_date']}")
    logger.info(f"Try number: {ti.try_number}")

    try:
        result = risky_operation()
        logger.info(f"Operation succeeded: {result}")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        raise
```

## Dashboard Examples

### Key Metrics to Track

1. **Pipeline Health**
   - DAG success rate (last 7 days)
   - Average DAG duration
   - Failed task count
   - Active DAG runs

2. **Performance**
   - Task duration trends
   - Queue wait time
   - Worker utilization
   - Database connection pool

3. **SLAs**
   - SLA compliance rate
   - SLA miss count
   - Average delay

4. **Resource Usage**
   - CPU utilization
   - Memory usage
   - Disk I/O
   - Network throughput

## Troubleshooting Common Issues

### High Scheduler Latency
- **Symptoms**: DAGs starting late, tasks queuing
- **Solutions**:
  - Reduce DAG parsing frequency
  - Simplify DAG files
  - Increase scheduler resources
  - Use HA scheduler setup

### Task Failures
- **Symptoms**: Tasks failing repeatedly
- **Solutions**:
  - Check task logs for errors
  - Verify resource availability
  - Review retry configuration
  - Implement better error handling

### Memory Issues
- **Symptoms**: Tasks killed by OOM
- **Solutions**:
  - Process data in batches
  - Use appropriate executor
  - Increase worker memory
  - Implement memory profiling

## Next Steps

- Explore [Notification Examples](../dags/06_notifications/)
- Review [Best Practices](best-practices.md)
- Check [Integration Examples](../dags/07_integrations/)
