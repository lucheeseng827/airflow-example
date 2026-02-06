"""
Database Integration Example

Demonstrates integration with various databases:
- PostgreSQL
- MySQL
- MongoDB
- Redis (caching)
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "database_integration",
    default_args=default_args,
    description="Database integration examples",
    schedule_interval="@hourly",
    catchup=False,
    tags=["database", "integration", "postgres", "mysql", "mongodb"],
)


def query_postgres(**context):
    """
    Query PostgreSQL database.

    In production:
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    records = postgres_hook.get_records(
        sql='SELECT * FROM users WHERE created_at >= %s',
        parameters=[context['ds']]
    )
    """
    execution_date = context["ds"]

    print("Connecting to PostgreSQL...")
    print(f"Query: SELECT * FROM users WHERE created_at >= '{execution_date}'")
    print("✓ Retrieved 500 records from PostgreSQL")

    return {"source": "postgres", "records": 500}


def query_mysql(**context):
    """
    Query MySQL database.

    In production:
    from airflow.providers.mysql.hooks.mysql import MySqlHook

    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    df = mysql_hook.get_pandas_df(
        sql='SELECT * FROM products WHERE updated_at >= %s',
        parameters=[context['ds']]
    )
    """
    execution_date = context["ds"]

    print("Connecting to MySQL...")
    print(f"Query: SELECT * FROM products WHERE updated_at >= '{execution_date}'")
    print("✓ Retrieved 250 records from MySQL")

    return {"source": "mysql", "records": 250}


def query_mongodb(**context):
    """
    Query MongoDB.

    In production:
    from airflow.providers.mongo.hooks.mongo import MongoHook

    mongo_hook = MongoHook(conn_id='mongo_default')
    collection = mongo_hook.get_collection('events', 'analytics')

    results = collection.find({
        'timestamp': {'$gte': context['execution_date']}
    })
    """
    execution_date = context["ds"]

    print("Connecting to MongoDB...")
    print(f"Collection: analytics.events")
    print(f"Filter: timestamp >= '{execution_date}'")
    print("✓ Retrieved 1000 documents from MongoDB")

    return {"source": "mongodb", "records": 1000}


def cache_in_redis(**context):
    """
    Cache results in Redis.

    In production:
    from airflow.providers.redis.hooks.redis import RedisHook

    redis_hook = RedisHook(redis_conn_id='redis_default')
    redis_conn = redis_hook.get_conn()

    redis_conn.setex(
        name='pipeline:last_run',
        time=3600,  # TTL in seconds
        value=context['ds']
    )
    """
    from airflow.exceptions import AirflowException

    ti = context["task_instance"]

    # Validate XCom pulls
    postgres_data = ti.xcom_pull(task_ids="query_postgres")
    mysql_data = ti.xcom_pull(task_ids="query_mysql")
    mongo_data = ti.xcom_pull(task_ids="query_mongodb")

    if postgres_data is None or "records" not in postgres_data:
        raise AirflowException(f"Failed to retrieve postgres data from XCom. Got: {postgres_data}")
    if mysql_data is None or "records" not in mysql_data:
        raise AirflowException(f"Failed to retrieve mysql data from XCom. Got: {mysql_data}")
    if mongo_data is None or "records" not in mongo_data:
        raise AirflowException(f"Failed to retrieve mongodb data from XCom. Got: {mongo_data}")

    total_records = postgres_data["records"] + mysql_data["records"] + mongo_data["records"]

    print("Caching results in Redis...")
    print(f"Key: pipeline:summary:{context['ds']}")
    print(f"Value: {total_records} total records")
    print("TTL: 24 hours")
    print("✓ Cached in Redis")


def insert_to_postgres(**context):
    """
    Insert aggregated data to PostgreSQL.

    In production:
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    postgres_hook.run(
        sql='INSERT INTO summary (date, total_records) VALUES (%s, %s)',
        parameters=[context['ds'], total_records]
    )
    """
    from airflow.exceptions import AirflowException

    ti = context["task_instance"]

    # Validate XCom pulls
    postgres_data = ti.xcom_pull(task_ids="query_postgres")
    mysql_data = ti.xcom_pull(task_ids="query_mysql")
    mongo_data = ti.xcom_pull(task_ids="query_mongodb")

    if postgres_data is None or "records" not in postgres_data:
        raise AirflowException(f"Failed to retrieve postgres data from XCom. Got: {postgres_data}")
    if mysql_data is None or "records" not in mysql_data:
        raise AirflowException(f"Failed to retrieve mysql data from XCom. Got: {mysql_data}")
    if mongo_data is None or "records" not in mongo_data:
        raise AirflowException(f"Failed to retrieve mongodb data from XCom. Got: {mongo_data}")

    total_records = postgres_data["records"] + mysql_data["records"] + mongo_data["records"]

    print("Inserting summary to PostgreSQL...")
    print(f"Table: summary")
    print(f"Date: {context['ds']}")
    print(f"Total Records: {total_records}")
    print("✓ Summary inserted")


# Extract from different databases in parallel
extract_postgres = PythonOperator(
    task_id="query_postgres",
    python_callable=query_postgres,
    dag=dag,
)

extract_mysql = PythonOperator(
    task_id="query_mysql",
    python_callable=query_mysql,
    dag=dag,
)

extract_mongo = PythonOperator(
    task_id="query_mongodb",
    python_callable=query_mongodb,
    dag=dag,
)

# Cache and store results
cache_results = PythonOperator(
    task_id="cache_in_redis",
    python_callable=cache_in_redis,
    dag=dag,
)

insert_summary = PythonOperator(
    task_id="insert_summary",
    python_callable=insert_to_postgres,
    dag=dag,
)

# Workflow - extract in parallel, then cache and insert
[extract_postgres, extract_mysql, extract_mongo] >> cache_results >> insert_summary
