from datetime import datetime, timedelta
import logging
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from ingestion.minio_to_snowflake import run_pipeline
from src.data_extraction import extract_countries_data, upload_to_minio
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator
import docker


def run_dbt():
    client = docker.from_env()

    container = client.containers.get("triplens-dbt")

    if container.status != "running":
        raise RuntimeError(
            f"triplens-dbt is not running. Current status: {container.status}"
        )

    result = container.exec_run(
        [
            "dbt",
            "run",
            "--project-dir",
            "/usr/app/triplens_dbt",
            "--profiles-dir",
            "/root/.dbt",
        ],
        workdir="/usr/app/triplens_dbt",
    )

    logs = result.output.decode("utf-8")
    print(logs)

    if result.exit_code != 0:
        raise RuntimeError(
            f"dbt run failed with exit code {result.exit_code}"
        )


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    'schedule_interval': '0 */4 * * *',

}


def extract_and_upload():
    """
    Extract countries data from REST Countries API
    and upload the raw JSON file to MinIO.
    """
    data = extract_countries_data()
    upload_to_minio(data)


def load_to_snowflake():
    """
    Load new JSON files from MinIO into Snowflake.
    Uses the watermark table to identify new files.
    """
    run_pipeline()


with DAG(
    dag_id="countries_ingestion",
    default_args=default_args,
    description="Validation DAG for Triplens Airflow orchestration layer",
    schedule_interval="0 */4 * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    max_active_runs=1,
    tags=["triplens",
          "countries",
          "minio",
          "snowflake",],
) as dag:

    extract_to_minio = PythonOperator(
        task_id="extract_to_minio",
        python_callable=extract_and_upload,
    )

    load_to_snowflake_task = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_to_snowflake,
    )

    dbt_run = PythonOperator(
        task_id="dbt_run",
        python_callable=run_dbt,
    )

    # Task dependency pipeline
    extract_to_minio >> load_to_snowflake_task >> dbt_run
