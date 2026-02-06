"""
AWS Integration Example

Demonstrates integration with AWS services:
- S3: File upload/download
- Lambda: Invoke serverless functions
- SageMaker: ML model deployment
- Redshift: Data warehouse operations
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "aws_integration",
    default_args=default_args,
    description="AWS services integration examples",
    schedule_interval="@daily",
    catchup=False,
    tags=["aws", "integration", "cloud"],
)


def upload_to_s3(**context):
    """
    Upload data to S3.

    In production:
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.load_file(
        filename='/path/to/file.csv',
        key='data/file.csv',
        bucket_name='my-bucket',
        replace=True
    )
    """
    execution_date = context["ds"]
    bucket = "my-data-bucket"
    key = f"data/processed/{execution_date}/output.csv"

    print(f"Uploading to S3...")
    print(f"Bucket: {bucket}")
    print(f"Key: {key}")
    print("✓ File uploaded to S3")

    return f"s3://{bucket}/{key}"


def download_from_s3(**context):
    """
    Download data from S3.

    In production:
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.download_file(
        key='data/input.csv',
        bucket_name='my-bucket',
        local_path='/tmp/input.csv'
    )
    """
    bucket = "my-data-bucket"
    key = "data/input/raw_data.csv"

    print(f"Downloading from S3...")
    print(f"Bucket: {bucket}")
    print(f"Key: {key}")
    print("✓ File downloaded from S3")


def invoke_lambda(**context):
    """
    Invoke AWS Lambda function.

    In production:
    from airflow.providers.amazon.aws.hooks.lambda_function import LambdaHook

    lambda_hook = LambdaHook(
        function_name='my-function',
        aws_conn_id='aws_default'
    )

    response = lambda_hook.invoke_lambda(
        payload='{"key": "value"}'
    )
    """
    function_name = "data-processor"
    payload = {"execution_date": context["ds"], "task": "process_data"}

    print(f"Invoking Lambda function: {function_name}")
    print(f"Payload: {payload}")
    print("✓ Lambda function invoked successfully")

    return {"status": "success", "records_processed": 1000}


def run_redshift_query(**context):
    """
    Execute query on Redshift.

    In production:
    from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator

    RedshiftDataOperator(
        task_id='run_query',
        cluster_identifier='my-cluster',
        database='mydb',
        db_user='admin',
        sql='SELECT * FROM users WHERE created_at >= {{ ds }}',
        aws_conn_id='aws_default'
    )

    Or use parameterized queries:
    from airflow.providers.amazon.aws.hooks.redshift_sql import RedshiftSQLHook

    redshift_hook = RedshiftSQLHook(redshift_conn_id='redshift_default')
    redshift_hook.run(
        sql='INSERT INTO fact_events SELECT * FROM staging_events WHERE event_date = %s',
        parameters=[context['ds']]
    )
    """
    execution_date = context["ds"]

    # WARNING: This example uses string formatting for demonstration only.
    # In production, ALWAYS use parameterized queries to prevent SQL injection.
    # Example: cursor.execute(sql, (execution_date,))
    query = f"""
    INSERT INTO fact_events
    SELECT * FROM staging_events
    WHERE event_date = '{execution_date}'
    """

    print("Executing Redshift query...")
    print(f"Query: {query}")
    print("⚠️  Note: In production, use parameterized queries!")
    print("✓ Redshift query executed successfully")


def deploy_sagemaker_model(**context):
    """
    Deploy model to SageMaker.

    In production:
    from airflow.providers.amazon.aws.operators.sagemaker import SageMakerEndpointOperator

    SageMakerEndpointOperator(
        task_id='deploy_model',
        config={
            'EndpointConfigName': 'my-endpoint-config',
            'EndpointName': 'my-endpoint',
        },
        aws_conn_id='aws_default'
    )
    """
    model_name = "customer-churn-model"
    endpoint_name = "churn-prediction-endpoint"

    print(f"Deploying model to SageMaker...")
    print(f"Model: {model_name}")
    print(f"Endpoint: {endpoint_name}")
    print("✓ Model deployed to SageMaker")

    return f"https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/{endpoint_name}/invocations"


# Tasks
download_data = PythonOperator(
    task_id="download_from_s3",
    python_callable=download_from_s3,
    dag=dag,
)

process_with_lambda = PythonOperator(
    task_id="invoke_lambda",
    python_callable=invoke_lambda,
    dag=dag,
)

upload_results = PythonOperator(
    task_id="upload_to_s3",
    python_callable=upload_to_s3,
    dag=dag,
)

load_to_redshift = PythonOperator(
    task_id="load_to_redshift",
    python_callable=run_redshift_query,
    dag=dag,
)

deploy_model = PythonOperator(
    task_id="deploy_sagemaker_model",
    python_callable=deploy_sagemaker_model,
    dag=dag,
)

# Workflow
download_data >> process_with_lambda >> upload_results >> load_to_redshift
upload_results >> deploy_model
