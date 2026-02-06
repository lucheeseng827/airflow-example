from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['nick@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('s3sync', default_args=default_args, schedule_interval=timedelta(minutes=30))


t1 = BashOperator(
    task_id='print_date',
    bash_command='echo "date" >> date.txt',
    dag=dag)

t2 = BashOperator(
    task_id='s3_sync_from_s3',
    bash_command='aws s3 sync s3://<bucket>/ /<path>',
    retries=3,
    dag=dag)


t2.set_upstream(t1)


