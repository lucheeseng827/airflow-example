"""
ML Model Training Pipeline

End-to-end machine learning pipeline:
- Extract training data
- Feature engineering
- Data validation
- Model training with hyperparameter tuning
- Model evaluation
- Model registration
- Deploy to production
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    "owner": "ml-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["ml-team@example.com"],
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "ml_model_training",
    default_args=default_args,
    description="Train and deploy ML model",
    schedule_interval="0 0 * * 0",  # Weekly on Sunday
    catchup=False,
    tags=["ml", "training", "model"],
)


def extract_training_data(**context):
    """Extract data for model training."""
    print("Extracting training data from data warehouse...")
    # Simulated: SQL query to get training data
    print("✓ Extracted 100,000 training samples")
    return {"rows": 100000, "features": 50}


def feature_engineering(**context):
    """Create features for ML model."""
    ti = context["task_instance"]
    data_info = ti.xcom_pull(task_ids="extract_data")

    print(f"Engineering features from {data_info['rows']} rows...")
    print("Creating: text embeddings, numerical scaling, categorical encoding")
    print("✓ Feature engineering completed - 75 features created")

    return {"total_features": 75, "rows": data_info["rows"]}


def validate_data(**context):
    """Validate data quality for training."""
    ti = context["task_instance"]
    features = ti.xcom_pull(task_ids="feature_engineering")

    print("Validating data quality...")
    print(f"Checking {features['rows']} rows, {features['total_features']} features")

    # Simulated checks
    null_percentage = 0.5
    duplicate_percentage = 0.1

    print(f"Null values: {null_percentage}%")
    print(f"Duplicates: {duplicate_percentage}%")

    if null_percentage > 5 or duplicate_percentage > 2:
        raise ValueError("Data quality checks failed!")

    print("✓ Data validation passed")


def train_model(**context):
    """Train ML model."""
    print("Training model...")
    print("Algorithm: Random Forest")
    print("Parameters: n_estimators=100, max_depth=10")

    # Simulated training
    print("Epoch 1/10: loss=0.45, accuracy=0.82")
    print("Epoch 5/10: loss=0.23, accuracy=0.91")
    print("Epoch 10/10: loss=0.15, accuracy=0.95")

    print("✓ Model training completed")

    return {
        "model_id": "rf_model_v1.2.3",
        "accuracy": 0.95,
        "loss": 0.15,
    }


def evaluate_model(**context):
    """Evaluate model performance."""
    ti = context["task_instance"]
    model_info = ti.xcom_pull(task_ids="train_model")

    print(f"Evaluating model: {model_info['model_id']}")
    print("Running on test set...")

    # Simulated evaluation metrics
    metrics = {
        "accuracy": 0.94,
        "precision": 0.93,
        "recall": 0.95,
        "f1_score": 0.94,
        "auc_roc": 0.96,
    }

    print("Test Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

    print("✓ Model evaluation completed")
    return metrics


def check_model_performance(**context):
    """Decide if model should be deployed based on performance."""
    ti = context["task_instance"]
    metrics = ti.xcom_pull(task_ids="evaluate_model")

    # Decision threshold
    min_accuracy = 0.90
    min_auc = 0.85

    if metrics["accuracy"] >= min_accuracy and metrics["auc_roc"] >= min_auc:
        print(f"✓ Model meets criteria (accuracy: {metrics['accuracy']}, AUC: {metrics['auc_roc']})")
        return "register_model"
    else:
        print(f"✗ Model below threshold (accuracy: {metrics['accuracy']}, AUC: {metrics['auc_roc']})")
        return "notify_poor_performance"


def register_model(**context):
    """Register model in model registry."""
    ti = context["task_instance"]
    model_info = ti.xcom_pull(task_ids="train_model")

    print(f"Registering model: {model_info['model_id']}")
    print("Model registry: s3://ml-models/production/")
    print("✓ Model registered successfully")


def deploy_model(**context):
    """Deploy model to production."""
    ti = context["task_instance"]
    model_info = ti.xcom_pull(task_ids="train_model")

    print(f"Deploying model: {model_info['model_id']}")
    print("Deployment target: Kubernetes cluster")
    print("Creating model serving endpoint...")
    print("✓ Model deployed - endpoint: https://api.example.com/predict")


def send_success_notification():
    """Send success notification."""
    print("📧 Sending deployment notification...")
    print("New model deployed successfully!")


def send_failure_notification():
    """Send failure notification."""
    print("🚨 Model performance below threshold - retraining recommended")


# Define tasks
start = DummyOperator(task_id="start", dag=dag)

extract_data = PythonOperator(
    task_id="extract_data",
    python_callable=extract_training_data,
    provide_context=True,
    dag=dag,
)

engineer_features = PythonOperator(
    task_id="feature_engineering",
    python_callable=feature_engineering,
    provide_context=True,
    dag=dag,
)

validate = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)

train = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

evaluate = PythonOperator(
    task_id="evaluate_model",
    python_callable=evaluate_model,
    provide_context=True,
    dag=dag,
)

check_performance = BranchPythonOperator(
    task_id="check_performance",
    python_callable=check_model_performance,
    provide_context=True,
    dag=dag,
)

register = PythonOperator(
    task_id="register_model",
    python_callable=register_model,
    provide_context=True,
    dag=dag,
)

deploy = PythonOperator(
    task_id="deploy_model",
    python_callable=deploy_model,
    provide_context=True,
    dag=dag,
)

notify_success = PythonOperator(
    task_id="notify_success",
    python_callable=send_success_notification,
    dag=dag,
)

notify_poor_performance = PythonOperator(
    task_id="notify_poor_performance",
    python_callable=send_failure_notification,
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag, trigger_rule="none_failed_min_one_success")

# Workflow
start >> extract_data >> engineer_features >> validate >> train >> evaluate
evaluate >> check_performance
check_performance >> register >> deploy >> notify_success >> end
check_performance >> notify_poor_performance >> end
