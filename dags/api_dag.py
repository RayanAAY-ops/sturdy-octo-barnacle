from datetime import datetime
from airflow.models import DAG 
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import json

import logging
import boto3
from botocore.exceptions import ClientError
import os


def save_posts_s3(ti,
                  file_name='responses.json',
                  bucket='airflow-practice-rayanaay',
                  object_name=None):
    posts = ti.xcom_pull(task_ids=['get_posts'])

    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket, f'{str(datetime.today())}_responses.json')

    s3object.put(
        Body=(bytes(json.dumps(posts[0]).encode('UTF-8')))
    )

def save_posts(ti) -> None:
    with open('/home/rayanaay/airflow/data/responses.json', 'w') as f:
        json.dump(posts[0], f)
    
with DAG(
    dag_id='api_dag',
    schedule_interval='@hourly',
    start_date=datetime(2024, 4, 22),
    catchup=False
) as dag:
    task_is_api_active = HttpSensor(
        task_id='is_api_active',
        http_conn_id='api_posts',
        endpoint='posts/'
    )

    task_get_posts = SimpleHttpOperator(
        task_id="get_posts",
        http_conn_id="api_posts",
        method='GET',
        endpoint='posts/',
        response_filter=lambda response: json.loads(response.text),
        log_response = True,
        # auth_type: Type[AuthBase] = HTTPBasicAuth,
    )

    task_save  = PythonOperator(
        task_id="save_posts",
        python_callable=save_posts_s3,

    )

    task_is_api_active >> task_get_posts >> task_save
