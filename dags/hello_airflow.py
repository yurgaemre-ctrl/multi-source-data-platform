from airflow.sdk import DAG, task
from datetime import datetime


with DAG(
    dag_id="hello_airflow",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
):

    @task
    def hello():
        print("Airflow successfully executed my first task.")

    hello()