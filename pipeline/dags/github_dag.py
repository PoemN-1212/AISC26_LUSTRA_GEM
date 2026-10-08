from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
from gem_pipeline.ingestion.github import fetch_github_projects

default_args = {
    'owner': 'PoemN',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='gem_github_projects_crawler',
    default_args=default_args,
    start_date=datetime(2026, 9, 25),
    schedule_interval='0 8 * * *',
    catchup=False,
    tags=['ingestion', 'github', 'cloud_db', 'local_db'],
) as dag:

    crawl_task = PythonOperator(
        task_id='fetch_projects_and_readme',
        python_callable=fetch_github_projects,
        execution_timeout=timedelta(hours=1)
    )
