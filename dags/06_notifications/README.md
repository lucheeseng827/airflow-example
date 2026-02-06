# 06 - Notifications & Alerts

Learn to implement comprehensive notification strategies for pipeline monitoring and alerting.

## Examples in This Directory

### slack_notifications.py
**Difficulty:** Intermediate
**Topics:** Slack integration, Callbacks, Custom messages

Slack notification patterns:
- **Failure Alerts**: Immediate notification on task failures
- **Success Notifications**: Confirm critical task completion
- **Retry Alerts**: Track when tasks are retrying
- **Custom Messages**: Rich formatted messages with data
- **Channel Routing**: Different alerts to different channels

### email_notifications.py
**Difficulty:** Intermediate
**Topics:** Email, EmailOperator, HTML formatting, Digest reports

Email notification patterns:
- **Simple Notifications**: Basic email alerts
- **HTML Emails**: Rich formatted emails with tables
- **Daily Digests**: Aggregated reports
- **Failure Details**: Comprehensive error information

## Notification Strategies

### 1. Failure Callbacks
Immediate alerts when tasks fail:
```python
def on_failure_callback(context):
    send_slack_alert(
        channel='#incidents',
        message=f"🚨 Task {context['task'].task_id} failed!"
    )

task = PythonOperator(
    task_id='critical_task',
    on_failure_callback=on_failure_callback
)
```

### 2. Success Callbacks
Confirm important completions:
```python
def on_success_callback(context):
    send_notification(
        f"✅ {context['task'].task_id} completed in {context['ti'].duration}s"
    )
```

### 3. Retry Callbacks
Track retry attempts:
```python
def on_retry_callback(context):
    if context['ti'].try_number >= 2:
        send_warning(f"Task retrying (attempt {context['ti'].try_number})")
```

### 4. SLA Miss Callbacks
Alert on SLA violations:
```python
def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    send_pagerduty_alert(
        severity='warning',
        summary=f'SLA missed for {len(slas)} tasks'
    )
```

## Notification Channels

### Slack
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

send_slack = SlackWebhookOperator(
    task_id='send_notification',
    slack_webhook_conn_id='slack_webhook',
    message='Pipeline completed!',
    channel='#data-alerts'
)
```

**Setup:**
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add connection in Airflow UI: Admin → Connections
3. Connection ID: `slack_webhook`
4. Connection Type: `Slack Webhook`
5. Host: Your webhook URL

### Email
```python
from airflow.operators.email import EmailOperator

send_email = EmailOperator(
    task_id='send_report',
    to=['team@example.com'],
    subject='Daily Report',
    html_content='<h1>Report</h1><p>{{ ds }}</p>'
)
```

**Setup (airflow.cfg):**
```ini
[smtp]
smtp_host = smtp.gmail.com
smtp_port = 587
smtp_starttls = True
smtp_ssl = False
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_mail_from = airflow@example.com
```

### PagerDuty
```python
def trigger_pagerduty(context):
    """Send incident to PagerDuty."""
    import requests

    response = requests.post(
        'https://events.pagerduty.com/v2/enqueue',
        json={
            'routing_key': 'YOUR_ROUTING_KEY',
            'event_action': 'trigger',
            'payload': {
                'summary': f"Task {context['task'].task_id} failed",
                'severity': 'error',
                'source': 'airflow',
            }
        }
    )
```

### Microsoft Teams
```python
def send_teams_message(webhook_url, message):
    """Send message to Microsoft Teams."""
    import requests

    requests.post(
        webhook_url,
        json={
            '@type': 'MessageCard',
            'summary': 'Airflow Alert',
            'sections': [{
                'activityTitle': message,
                'activitySubtitle': 'From Airflow'
            }]
        }
    )
```

### Discord
```python
def send_discord_message(webhook_url, message):
    """Send message to Discord."""
    import requests

    requests.post(
        webhook_url,
        json={'content': message}
    )
```

## Alert Patterns

### 1. Immediate Critical Alerts
For production failures requiring immediate attention:
```python
def critical_failure(context):
    send_pagerduty_alert(severity='critical')
    send_slack_alert(channel='#incidents', mention='@oncall')
    send_sms_alert(phone='+1234567890')
```

### 2. Throttled Warnings
Prevent alert fatigue:
```python
def throttled_alert(context):
    task_id = context['task'].task_id
    last_alert = get_last_alert_time(task_id)

    # Only alert once per hour
    if not last_alert or (now() - last_alert) > timedelta(hours=1):
        send_alert(context)
        record_alert_time(task_id, now())
```

### 3. Digest Reports
Aggregate multiple events:
```python
def daily_digest(**context):
    failures = get_failures_last_24h()
    summary = generate_summary(failures)

    send_email(
        to='team@example.com',
        subject='Daily Airflow Digest',
        body=summary
    )
```

### 4. Conditional Alerts
Alert based on conditions:
```python
def conditional_alert(context):
    ti = context['ti']
    duration = ti.duration

    # Only alert if task took longer than expected
    if duration > timedelta(hours=2).total_seconds():
        send_alert(f'Task took {duration}s (expected < 2h)')
```

## Message Formatting

### Rich Slack Messages
```python
def send_rich_slack_message(context):
    from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

    slack = SlackWebhookHook(slack_webhook_conn_id='slack')

    blocks = [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': '🚨 Task Failed'}
        },
        {
            'type': 'section',
            'fields': [
                {'type': 'mrkdwn', 'text': f"*DAG:*\n{context['dag'].dag_id}"},
                {'type': 'mrkdwn', 'text': f"*Task:*\n{context['task'].task_id}"},
            ]
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': 'View Logs'},
                    'url': context['ti'].log_url
                }
            ]
        }
    ]

    slack.send(blocks=blocks)
```

### HTML Email Templates
```python
html_template = """
<html>
<head>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #4CAF50; color: white; }
        .success { color: green; }
        .failure { color: red; }
    </style>
</head>
<body>
    <h2>Pipeline Report</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Status</td><td class="success">Success</td></tr>
        <tr><td>Duration</td><td>{{ duration }}</td></tr>
        <tr><td>Records</td><td>{{ records }}</td></tr>
    </table>
</body>
</html>
"""
```

## Best Practices

1. **Alert Levels**: Use severity levels (info, warning, error, critical)
2. **Avoid Fatigue**: Don't over-alert; use throttling and digests
3. **Context**: Include relevant details (logs, metrics, timestamps)
4. **Actionable**: Make alerts actionable with links and next steps
5. **Testing**: Test notification channels before production
6. **Redundancy**: Use multiple channels for critical alerts
7. **On-call**: Route critical alerts to on-call rotation

## Testing Notifications

```bash
# Test a task with notifications
airflow tasks test slack_notifications send_slack_summary 2024-01-01

# Trigger entire DAG
airflow dags trigger email_notifications
```

## Next Steps

- Set up Slack/Email connections
- Configure on-call rotations
- Implement alert escalation
- Create custom notification operators
- Build alert dashboards
- Review [Monitoring Guide](../../docs/monitoring-guide.md)

## Resources

- [Airflow Slack Provider](https://airflow.apache.org/docs/apache-airflow-providers-slack/)
- [Email Configuration](https://airflow.apache.org/docs/apache-airflow/stable/howto/email-config.html)
- [Best Practices](../../docs/best-practices.md)
