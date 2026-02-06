# 03 - ML Pipelines

Machine Learning pipeline orchestration for ML Engineers. Learn to automate training, evaluation, and deployment workflows.

## Examples in This Directory

### model_training.py
**Difficulty:** Intermediate to Advanced
**Topics:** ML Training, Model Evaluation, Deployment, BranchPythonOperator

End-to-end ML pipeline:
- **Data Extraction**: Pull training data from warehouse
- **Feature Engineering**: Create and transform features
- **Data Validation**: Quality checks before training
- **Model Training**: Train ML model with hyperparameters
- **Model Evaluation**: Test performance metrics
- **Conditional Deployment**: Deploy only if metrics meet threshold
- **Model Registry**: Register successful models
- **Production Deployment**: Deploy to serving endpoint

**Schedule:** Weekly on Sundays
```bash
airflow dags test ml_model_training 2024-01-01
```

## ML Pipeline Stages

### 1. Data Preparation
```python
extract_data = PythonOperator(
    task_id='extract_training_data',
    python_callable=extract_from_warehouse
)

engineer_features = PythonOperator(
    task_id='feature_engineering',
    python_callable=create_features
)
```

### 2. Training
```python
train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_random_forest,
    # Use pools for GPU resources
    pool='gpu_pool'
)
```

### 3. Evaluation
```python
evaluate = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_on_test_set
)
```

### 4. Conditional Deployment
```python
check_metrics = BranchPythonOperator(
    task_id='check_performance',
    python_callable=lambda **ctx:
        'deploy' if get_accuracy() > 0.90 else 'retrain'
)
```

## Common ML Patterns

### Hyperparameter Tuning
```python
def tune_hyperparameters(**context):
    from sklearn.model_selection import GridSearchCV

    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15]
    }

    grid_search = GridSearchCV(model, param_grid)
    grid_search.fit(X_train, y_train)

    # Store best params in XCom
    context['ti'].xcom_push(key='best_params',
                            value=grid_search.best_params_)
```

### Feature Store Integration
```python
def save_features_to_store(**context):
    """Save engineered features for reuse."""
    features.to_parquet(
        f's3://feature-store/features_{context["ds"]}.parquet'
    )
```

### Model Versioning
```python
def register_model(**context):
    """Register model with metadata."""
    model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M')}"

    model_metadata = {
        'version': model_version,
        'accuracy': get_accuracy(),
        'training_date': context['ds'],
        'features': get_feature_list(),
    }

    save_to_registry(model, model_metadata)
```

### A/B Testing
```python
def deploy_for_ab_test(**context):
    """Deploy model for A/B testing."""
    # Deploy to 10% of traffic
    deploy_model(
        model_id=context['ti'].xcom_pull(key='model_id'),
        traffic_percentage=10
    )
```

## Integration with ML Tools

### MLflow
```python
import mlflow

def train_with_mlflow(**context):
    with mlflow.start_run():
        mlflow.log_params(params)

        model = train_model()

        mlflow.log_metrics({
            'accuracy': accuracy,
            'f1_score': f1
        })

        mlflow.sklearn.log_model(model, 'model')
```

### Weights & Biases
```python
import wandb

def train_with_wandb(**context):
    wandb.init(project='my-ml-project')

    wandb.config.update(hyperparameters)

    for epoch in range(epochs):
        loss = train_epoch()
        wandb.log({'loss': loss, 'epoch': epoch})
```

### SageMaker
```python
from airflow.providers.amazon.aws.operators.sagemaker import (
    SageMakerTrainingOperator
)

train = SageMakerTrainingOperator(
    task_id='train_sagemaker',
    config={
        'TrainingJobName': 'my-training-job',
        'AlgorithmSpecification': {...},
        'InputDataConfig': [...],
    }
)
```

### Kubeflow
```python
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator
)

train = KubernetesPodOperator(
    task_id='train_on_k8s',
    name='ml-training',
    image='my-ml-image:latest',
    namespace='ml-pipelines'
)
```

## Best Practices for ML Pipelines

### 1. Reproducibility
- Pin library versions
- Save random seeds
- Version control data snapshots
- Track all hyperparameters

### 2. Data Validation
- Check for data drift
- Validate feature distributions
- Ensure no data leakage
- Monitor data quality

### 3. Model Validation
- Separate train/validation/test sets
- Cross-validation for robustness
- Monitor for model drift
- Track performance over time

### 4. Resource Management
```python
# Use pools for GPU resources
default_args = {
    'pool': 'gpu_pool',  # Limit concurrent GPU jobs
}

# Set task execution timeout
task = PythonOperator(
    task_id='train',
    execution_timeout=timedelta(hours=4),
    pool_slots=2,  # Reserve 2 GPU slots
)
```

### 5. Experiment Tracking
- Log all experiments
- Track model lineage
- Save training artifacts
- Document model decisions

## Real-World Use Cases

### Automated Retraining
- Daily/weekly model updates
- Trigger on data drift
- Automatic deployment if metrics improve
- Fallback to previous model if regression

### Feature Engineering Pipeline
- Extract raw data
- Compute features
- Save to feature store
- Version features
- Validate feature quality

### Model Monitoring
- Track prediction accuracy
- Detect data/model drift
- Auto-retrain on drift
- Alert on anomalies

### Batch Prediction
- Load latest model
- Run predictions on new data
- Save results
- Quality checks on outputs

## Metrics to Track

- **Training Metrics**: Loss, accuracy, precision, recall, F1
- **Performance**: Training time, inference latency
- **Data Quality**: Missing values, outliers, distributions
- **Model Drift**: Prediction distributions over time
- **Business Metrics**: Revenue impact, user engagement

## Next Steps

- Integrate with your ML platform (MLflow, SageMaker, etc.)
- Add experiment tracking
- Implement model monitoring
- Set up A/B testing framework
- Explore [Monitoring](../05_monitoring/) for ML metrics
- Check [Integrations](../07_integrations/) for AWS SageMaker

## Resources

- [MLOps Best Practices](https://ml-ops.org/)
- [Airflow + MLflow](https://mlflow.org/docs/latest/index.html)
- [Best Practices](../../docs/best-practices.md)
