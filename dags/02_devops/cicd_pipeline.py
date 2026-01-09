"""
CI/CD Pipeline Example

Demonstrates a continuous integration and deployment workflow:
- Run tests
- Build application
- Deploy to staging
- Run integration tests
- Deploy to production
- Send notifications
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    "owner": "devops-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["devops@example.com"],
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "cicd_pipeline",
    default_args=default_args,
    description="CI/CD deployment pipeline",
    schedule_interval=None,  # Triggered manually or by webhook
    catchup=False,
    tags=["devops", "cicd", "deployment"],
)


def check_tests_passed(**context):
    """Check if tests passed and decide next step."""
    # In real scenario, check test results
    tests_passed = True  # Simulated

    if tests_passed:
        return "build_application"
    else:
        return "notify_failure"


def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    # Simulated test execution
    print("✓ All 150 tests passed")
    return True


def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    # Simulated integration tests
    print("✓ Integration tests passed")
    return True


def deploy_to_environment(environment):
    """Deploy application to specified environment."""

    def deploy(**context):
        print(f"Deploying to {environment}...")
        print(f"Version: {context['run_id']}")
        print(f"✓ Deployment to {environment} successful!")
        return f"Deployed to {environment}"

    return deploy


def send_success_notification():
    """Send success notification."""
    print("📧 Sending success notification...")
    print("✓ Deployment successful - all systems operational")


def send_failure_notification():
    """Send failure notification."""
    print("🚨 Sending failure notification...")
    print("✗ Pipeline failed - check logs for details")


# Start task
start = DummyOperator(task_id="start", dag=dag)

# Run tests
unit_tests = PythonOperator(
    task_id="run_unit_tests",
    python_callable=run_unit_tests,
    dag=dag,
)

# Linting and code quality
lint_code = BashOperator(
    task_id="lint_code",
    bash_command='echo "Running linter... ✓ No issues found"',
    dag=dag,
)

# Security scan
security_scan = BashOperator(
    task_id="security_scan",
    bash_command='echo "Running security scan... ✓ No vulnerabilities"',
    dag=dag,
)

# Decision point
check_tests = BranchPythonOperator(
    task_id="check_tests",
    python_callable=check_tests_passed,
    provide_context=True,
    dag=dag,
)

# Build application
build = BashOperator(
    task_id="build_application",
    bash_command='echo "Building Docker image... ✓ Build successful"',
    dag=dag,
)

# Deploy to staging
deploy_staging = PythonOperator(
    task_id="deploy_staging",
    python_callable=deploy_to_environment("staging"),
    provide_context=True,
    dag=dag,
)

# Integration tests on staging
integration_tests = PythonOperator(
    task_id="integration_tests",
    python_callable=run_integration_tests,
    dag=dag,
)

# Deploy to production
deploy_production = PythonOperator(
    task_id="deploy_production",
    python_callable=deploy_to_environment("production"),
    provide_context=True,
    dag=dag,
)

# Notifications
notify_success = PythonOperator(
    task_id="notify_success",
    python_callable=send_success_notification,
    dag=dag,
)

notify_failure = PythonOperator(
    task_id="notify_failure",
    python_callable=send_failure_notification,
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag, trigger_rule="none_failed_min_one_success")

# Define workflow
start >> [unit_tests, lint_code, security_scan] >> check_tests
check_tests >> build >> deploy_staging >> integration_tests >> deploy_production
deploy_production >> notify_success >> end
check_tests >> notify_failure >> end
