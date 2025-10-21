from datetime import datetime
from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator

# Create the DAG
dag = DAG(
    "ingestion",
    start_date=datetime(2024, 1, 1),
    description="Manual DAG to run AWS Batch job with Python image and main.py script",
    catchup=False,
    tags=["ingestion", "python"],
)

# AWS Batch job task
transformation = BatchOperator(
    task_id="ignestion-task-1",
    job_name="transformation-job",
    job_definition="ingestion-job",
    job_queue="dpstack-batch-queue",
    region_name="eu-west-1",
    container_overrides={"command": ["python", "spacex/transformation.py"]},
    dag=dag,
)

copy_job = BatchOperator(
    task_id="ignestion-task-2",
    job_name="copy-job",
    job_definition="ingestion-job",
    job_queue="dpstack-batch-queue",
    region_name="eu-west-1",
    container_overrides={"command": ["python", "spacex/ingest.py"]},
    dag=dag,
)

# Set the task (no dependencies since it's a single task)
transformation >> copy_job
