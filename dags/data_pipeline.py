from airflow.sdk import DAG, task
from datetime import datetime
import subprocess


with DAG(
    dag_id="data_pipeline",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
):

    @task
    def ingest_fred():
        subprocess.run(
            ["python", "/opt/airflow/src/ingest_fred.py"],
            check=True,
        )

    @task
    def ingest_yahoo():
        subprocess.run(
            ["python", "/opt/airflow/src/ingest_yahoo.py"],
            check=True,
        )

    @task
    def ingest_tiingo():
        subprocess.run(
            ["python", "/opt/airflow/src/ingest_tiingo.py"],
            check=True,
        )
    @task
    def load_staging_market():
        subprocess.run(
            [
                "python",
                "/opt/airflow/src/run_sql.py",
                "/opt/airflow/sql/staging/002_load_staging_market.sql",
            ],
            check=True,
        )
    @task
    def load_curated_market():
        sql_files = [
            "/opt/airflow/sql/curated/001_create_star_schema.sql",
            "/opt/airflow/sql/curated/002_load_dimensions.sql",
            "/opt/airflow/sql/curated/003_load_fact_market.sql",
        ]

        for sql_file in sql_files:
            subprocess.run(
                [
                    "python",
                    "/opt/airflow/src/run_sql.py",
                    sql_file,
                ],
                check=True,
            )
    @task
    def load_curated_macro():
        sql_files = [
            "/opt/airflow/sql/curated/004_create_macro_fact.sql",
            "/opt/airflow/sql/curated/005_load_macro.sql",
        ]

        for sql_file in sql_files:
            subprocess.run(
                [
                    "python",
                    "/opt/airflow/src/run_sql.py",
                    sql_file,
                ],
                check=True,
            )
    @task
    def run_data_quality_tests():
        subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "/opt/airflow/tests/test_data_quality.py",
                "-q",
            ],
            check=True,
        )
    fred = ingest_fred()
    yahoo = ingest_yahoo()
    tiingo = ingest_tiingo()
    staging = load_staging_market()
    curated_market = load_curated_market()

    [yahoo, tiingo] >> staging >> curated_market

    curated_macro = load_curated_macro()
    [fred, curated_market] >> curated_macro
    dq = run_data_quality_tests()
    [curated_market, curated_macro] >> dq