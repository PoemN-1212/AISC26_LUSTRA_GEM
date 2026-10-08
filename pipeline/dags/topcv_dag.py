from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
from gem_pipeline.ingestion.topcv import run_bulk_crawler

default_args = {
    'owner': 'PoemN',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='gem_topcv_daily_crawler',
    default_args=default_args,
    start_date=datetime(2026, 9, 25),
    schedule_interval='0 7 * * *',
    catchup=False,
    tags=['ingestion', 'big_data', 'flaresolverr'],
) as dag:

    crawl_task = PythonOperator(
        task_id='crawl_and_save_to_postgres',
        python_callable=run_bulk_crawler,
        execution_timeout=timedelta(hours=12)
    )
