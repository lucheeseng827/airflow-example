# 02 - DevOps Automation

Automation workflows for DevOps engineers. Learn to orchestrate CI/CD, backups, monitoring, and infrastructure tasks.

## Examples in This Directory

### cicd_pipeline.py
**Difficulty:** Intermediate
**Topics:** CI/CD, BranchPythonOperator, Testing, Deployment

Complete CI/CD pipeline showing:
- Running tests and code quality checks
- Branching logic based on test results
- Multi-stage deployments (staging → production)
- Success/failure notifications
- Security scanning

**Use Cases:**
- Automated application deployment
- Release management
- Quality gates
- Environment promotion

**Run it:**
```bash
airflow dags trigger cicd_pipeline
```

### backup_automation.py
**Difficulty:** Intermediate
**Topics:** Backup, S3, Data retention, XCom

Automated backup workflow:
- Database backups
- File system backups
- Compression and encryption
- Cloud storage upload (S3)
- Backup verification
- Automated cleanup of old backups

**Use Cases:**
- Daily database backups
- Disaster recovery
- Compliance requirements
- Data retention policies

**Schedule:** Daily at 2 AM
```bash
# Test the backup workflow
airflow dags test backup_automation 2024-01-01
```

## Key Concepts for DevOps

### 1. Triggered vs Scheduled DAGs
```python
# Scheduled (runs automatically)
schedule_interval='@daily'

# Manual trigger only (webhook/API)
schedule_interval=None
```

### 2. Branching Logic
Use `BranchPythonOperator` for conditional workflows:
```python
def decide_next_step(**context):
    if tests_passed:
        return 'deploy_staging'
    return 'notify_failure'
```

### 3. Parallel Execution
Run independent tasks simultaneously:
```python
start >> [run_tests, lint_code, security_scan] >> build
```

### 4. Retries and Fault Tolerance
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}
```

## Common DevOps Patterns

### Infrastructure as Code
```python
terraform_plan = BashOperator(
    task_id='terraform_plan',
    bash_command='cd /terraform && terraform plan'
)

terraform_apply = BashOperator(
    task_id='terraform_apply',
    bash_command='cd /terraform && terraform apply -auto-approve'
)
```

### Container Orchestration
```python
build_image = BashOperator(
    task_id='build_docker_image',
    bash_command='docker build -t myapp:{{ ds_nodash }} .'
)

push_image = BashOperator(
    task_id='push_to_registry',
    bash_command='docker push myapp:{{ ds_nodash }}'
)
```

### Health Checks
```python
def check_service_health():
    response = requests.get('https://api.example.com/health')
    if response.status_code != 200:
        raise Exception('Service unhealthy!')
```

## Integration Points

### Webhooks
Trigger DAGs from external systems:
```bash
curl -X POST \
  http://localhost:8080/api/v1/dags/cicd_pipeline/dagRuns \
  -H 'Content-Type: application/json' \
  -d '{"conf": {"commit_sha": "abc123"}}'
```

### External Systems
- **GitHub Actions**: Trigger Airflow DAGs from CI
- **Jenkins**: Orchestrate Jenkins jobs
- **Kubernetes**: Deploy to K8s clusters
- **Terraform**: Infrastructure provisioning
- **Ansible**: Configuration management

## Best Practices

1. **Idempotency**: Deployments should be repeatable
2. **Rollback Strategy**: Plan for failures
3. **Environment Separation**: dev → staging → prod
4. **Secret Management**: Use Airflow Connections/Variables
5. **Monitoring**: Track deployment success rates
6. **Notifications**: Alert on failures

## Real-World Use Cases

### Continuous Deployment
- Build and test application
- Deploy to staging
- Run integration tests
- Deploy to production
- Health checks
- Rollback if needed

### Backup and Recovery
- Database dumps
- File backups
- Encrypt and compress
- Upload to cloud storage
- Verify backups
- Cleanup old backups

### Infrastructure Maintenance
- Security patching
- Certificate renewal
- Log rotation
- Disk cleanup
- Database optimization

### Monitoring Automation
- Collect metrics
- Generate reports
- Check thresholds
- Auto-remediation
- Alert escalation

## Next Steps

- Add custom operators for your tools
- Integrate with your CI/CD platform
- Implement blue/green deployments
- Add canary deployment patterns
- Explore [Monitoring](../05_monitoring/) for observability
- Check [Notifications](../06_notifications/) for alerting

## Resources

- [Airflow API Documentation](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html)
- [Best Practices](../../docs/best-practices.md)
- [Testing Guide](../../docs/testing-guide.md)
