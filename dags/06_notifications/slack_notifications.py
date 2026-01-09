"""
Slack Notifications Example

Demonstrates various notification patterns with Slack:
- Task failure notifications
- Task success notifications
- Custom message formatting
- Conditional notifications
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


def send_slack_notification(message, channel="#data-alerts", username="Airflow Bot"):
    """
    Send notification to Slack.

    In production, use SlackWebhookOperator or SlackAPIPostOperator
    from airflow.providers.slack.operators.slack_webhook
    """
    print(f"📱 Sending Slack notification to {channel}")
    print(f"Message: {message}")
    print(f"From: {username}")

    # In production:
    # from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
    # slack_hook = SlackWebhookHook(slack_webhook_conn_id='slack_connection')
    # slack_hook.send(text=message, channel=channel, username=username)


def on_failure_callback(context):
    """Send Slack alert when task fails."""
    task_instance = context.get("task_instance")
    exception = context.get("exception")
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    execution_date = context.get("execution_date")
    log_url = context.get("task_instance").log_url

    message = f"""
🚨 *Task Failed*

*DAG*: {dag_id}
*Task*: {task_id}
*Execution Date*: {execution_date}
*Error*: {exception}
*Logs*: {log_url}

Please investigate immediately!
    """.strip()

    send_slack_notification(message, channel="#incidents")


def on_success_callback(context):
    """Send Slack notification when critical task succeeds."""
    task_instance = context.get("task_instance")
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    duration = task_instance.duration

    message = f"""
✅ *Task Completed Successfully*

*DAG*: {dag_id}
*Task*: {task_id}
*Duration*: {duration:.2f} seconds
    """.strip()

    send_slack_notification(message, channel="#data-updates")


def on_retry_callback(context):
    """Send Slack notification when task retries."""
    task_instance = context.get("task_instance")
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    try_number = task_instance.try_number

    message = f"""
⚠️ *Task Retry*

*DAG*: {dag_id}
*Task*: {task_id}
*Retry*: {try_number}
    """.strip()

    send_slack_notification(message, channel="#warnings")


def send_custom_slack_message(**context):
    """Send custom Slack message with data summary."""
    ti = context["task_instance"]

    # Simulate getting metrics
    records_processed = 10000
    execution_time = 45.2

    message = f"""
📊 *Daily ETL Summary*

*Records Processed*: {records_processed:,}
*Execution Time*: {execution_time}s
*Status*: Success ✅
*Date*: {context['ds']}

Dashboard: https://dashboard.example.com
    """.strip()

    send_slack_notification(message, channel="#daily-reports")


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
    "on_retry_callback": on_retry_callback,
}

dag = DAG(
    "slack_notifications",
    default_args=default_args,
    description="Slack notification examples",
    schedule_interval="@daily",
    catchup=False,
    tags=["notifications", "slack", "alerts"],
)

# Task with success callback
critical_task = PythonOperator(
    task_id="critical_processing",
    python_callable=lambda: print("Processing critical data..."),
    on_success_callback=on_success_callback,
    dag=dag,
)

# Task that might fail (for testing failure notifications)
risky_task = BashOperator(
    task_id="risky_operation",
    bash_command='echo "Running risky operation..." && sleep 2',
    dag=dag,
)

# Send custom summary notification
send_summary = PythonOperator(
    task_id="send_slack_summary",
    python_callable=send_custom_slack_message,
    provide_context=True,
    dag=dag,
)

critical_task >> risky_task >> send_summary
