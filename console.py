#!/usr/bin/env python3
import boto3
from datetime import datetime


def submit_dbt_run_job():
    """Submit dbt run job to AWS Batch"""

    # Initialize AWS Batch client
    batch_client = boto3.client("batch", region_name="eu-west-1")

    # Job parameters
    job_name = f"dbt-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    job_definition = "dbt-transformation-job"
    job_queue = "dpstack-batch-queue"  # Replace with actual queue name

    # Override command to run dbt
    overrides = {
        "command": ["dbt", "debug"],
        "environment": [
            {"name": "DBT_PROFILES_DIR", "value": "./"},
            {"name": "DBT_TARGET_PATH", "value": "dbt/target"},
            {"name": "DBT_LOG_PATH", "value": "dbt/logs"},
        ],
    }

    try:
        response = batch_client.submit_job(
            jobName=job_name,
            jobQueue=job_queue,
            jobDefinition=job_definition,
            parameters={},
            containerOverrides=overrides,
        )

        print("✅ Job submitted successfully!")
        print(f"Job ID: {response['jobId']}")
        print(f"Job Name: {response['jobName']}")
        return response["jobId"]

    except Exception as e:
        print(f"❌ Error submitting job: {str(e)}")
        return None


if __name__ == "__main__":
    submit_dbt_run_job()
