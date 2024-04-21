from datetime import datetime
from airflow.models import DAG 
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import json

def save_posts(ti) -> None:
    posts = ti.xcom_pull(task_ids=['get_posts'])
    with open('./responses.json', 'w') as f:
        json.dump(posts[0], f)
    
with DAG(
    dag_id='api_dag',
    schedule_interval='@daily',
    start_date=datetime(2024, 4, 21),
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
        python_callable=save_posts,

    )

    task_is_api_active >> task_get_posts >> task_save