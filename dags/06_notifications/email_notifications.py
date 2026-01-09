"""
Email Notifications Example

Demonstrates email notification patterns:
- Failure alerts
- Success notifications
- Daily digest reports
- Custom HTML emails with EmailOperator
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator


def send_custom_email(to, subject, body):
    """
    Send custom email.

    In production, use EmailOperator or send via SMTP
    """
    print(f"📧 Sending email to: {to}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")

    # In production, configure SMTP in airflow.cfg:
    # [smtp]
    # smtp_host = smtp.gmail.com
    # smtp_port = 587
    # smtp_user = your-email@gmail.com
    # smtp_password = your-password
    # smtp_mail_from = airflow@example.com


def on_failure_email(context):
    """Send detailed failure email."""
    task_instance = context.get("task_instance")
    exception = context.get("exception")

    subject = f"❌ Task Failed: {task_instance.task_id}"

    body = f"""
    <html>
    <body>
        <h2>Task Failure Alert</h2>

        <h3>Details:</h3>
        <ul>
            <li><strong>DAG:</strong> {task_instance.dag_id}</li>
            <li><strong>Task:</strong> {task_instance.task_id}</li>
            <li><strong>Execution Date:</strong> {context.get('execution_date')}</li>
            <li><strong>Try Number:</strong> {task_instance.try_number}</li>
        </ul>

        <h3>Error:</h3>
        <pre>{exception}</pre>

        <h3>Logs:</h3>
        <p><a href="{task_instance.log_url}">View logs</a></p>

        <hr>
        <p><em>This is an automated message from Airflow</em></p>
    </body>
    </html>
    """

    send_custom_email(
        to=["oncall@example.com", "data-team@example.com"],
        subject=subject,
        body=body,
    )


def generate_daily_digest(**context):
    """Generate and send daily digest email."""
    execution_date = context["ds"]

    # Simulated metrics
    metrics = {
        "dags_run": 12,
        "dags_success": 10,
        "dags_failed": 2,
        "tasks_run": 156,
        "tasks_success": 148,
        "tasks_failed": 8,
        "total_duration": "2h 34m",
    }

    subject = f"📊 Airflow Daily Digest - {execution_date}"

    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
        </style>
    </head>
    <body>
        <h2>Airflow Daily Digest</h2>
        <p><strong>Date:</strong> {execution_date}</p>

        <h3>Summary</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>DAGs Run</td>
                <td>{metrics['dags_run']}</td>
            </tr>
            <tr>
                <td>DAGs Success</td>
                <td class="success">{metrics['dags_success']}</td>
            </tr>
            <tr>
                <td>DAGs Failed</td>
                <td class="failure">{metrics['dags_failed']}</td>
            </tr>
            <tr>
                <td>Tasks Run</td>
                <td>{metrics['tasks_run']}</td>
            </tr>
            <tr>
                <td>Tasks Success</td>
                <td class="success">{metrics['tasks_success']}</td>
            </tr>
            <tr>
                <td>Tasks Failed</td>
                <td class="failure">{metrics['tasks_failed']}</td>
            </tr>
            <tr>
                <td>Total Duration</td>
                <td>{metrics['total_duration']}</td>
            </tr>
        </table>

        <h3>Failed DAGs</h3>
        <ul>
            <li>customer_etl - Database connection timeout</li>
            <li>product_sync - API rate limit exceeded</li>
        </ul>

        <p><a href="http://localhost:8080">View Airflow Dashboard</a></p>

        <hr>
        <p><em>This is an automated daily digest from Airflow</em></p>
    </body>
    </html>
    """

    send_custom_email(
        to=["team@example.com"],
        subject=subject,
        body=body,
    )

    print("✓ Daily digest email sent")


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["alerts@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_email,
}

dag = DAG(
    "email_notifications",
    default_args=default_args,
    description="Email notification examples",
    schedule_interval="@daily",
    catchup=False,
    tags=["notifications", "email", "alerts"],
)

# Simple email notification using EmailOperator
send_simple_email = EmailOperator(
    task_id="send_simple_notification",
    to=["team@example.com"],
    subject="Pipeline Started",
    html_content="""
    <h3>Pipeline Execution Started</h3>
    <p>The daily ETL pipeline has started execution.</p>
    <p>Execution Date: {{ ds }}</p>
    """,
    dag=dag,
)

# Process data task
process_data = PythonOperator(
    task_id="process_data",
    python_callable=lambda: print("Processing data..."),
    dag=dag,
)

# Send daily digest
send_digest = PythonOperator(
    task_id="send_daily_digest",
    python_callable=generate_daily_digest,
    provide_context=True,
    dag=dag,
)

# Success notification
send_success_email = EmailOperator(
    task_id="send_success_notification",
    to=["team@example.com"],
    subject="✅ Pipeline Completed Successfully",
    html_content="""
    <h3>Pipeline Completed</h3>
    <p>The daily ETL pipeline completed successfully.</p>
    <p>Execution Date: {{ ds }}</p>
    <p>All tasks completed without errors.</p>
    """,
    dag=dag,
)

send_simple_email >> process_data >> send_digest >> send_success_email
