# airflow/dags/streaming_pipeline_dag.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from src.producers.social_media_producer import SocialMediaProducer
from src.producers.ecommerce_producer import EcommerceProducer
from src.processors.sentiment_analyzer import process_social_media_stream
from src.processors.user_behavior_processor import process_user_behavior

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'streaming_pipeline',
    default_args=default_args,
    description='Streaming data pipeline for social media and e-commerce data',
    schedule_interval=timedelta(days=1)
)

def start_social_media_producer():
    producer = SocialMediaProducer(bootstrap_servers='localhost:9092')
    producer.start_producing()

def start_ecommerce_producer():
    producer = EcommerceProducer(bootstrap_servers='localhost:9092')
    producer.start_producing()

start_social_media_task = PythonOperator(
    task_id='start_social_media_producer',
    python_callable=start_social_media_producer,
    dag=dag
)

start_ecommerce_task = PythonOperator(
    task_id='start_ecommerce_producer',
    python_callable=start_ecommerce_producer,
    dag=dag
)

process_social_media_task = PythonOperator(
    task_id='process_social_media',
    python_callable=process_social_media_stream,
    dag=dag
)

process_user_behavior_task = PythonOperator(
    task_id='process_user_behavior',
    python_callable=process_user_behavior,
    dag=dag
)

# Set task dependencies
[start_social_media_task, start_ecommerce_task] >> \
[process_social_media_task, process_user_behavior_task]