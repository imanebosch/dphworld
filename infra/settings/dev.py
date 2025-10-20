"""Settings for the development environment"""

import os

config = {
    "account": os.getenv("AWS_ACCOUNT_ID", None),
    "region": "eu-west-1",
    "name": "dpstack",
    "vpc": {"max_azs": 3, "nat_gateways": 1},
    "storage": {"name": "dpstack-dlake", "removal_policy": "DESTROY"},
    "mwaa": {
        "name": "dpstack-airflow",
        "bucket_name": "dpstack-airflow",
        "removal_policy": "DESTROY",
    },
    "redshift": {
        "namespace_name": "dpstack",
        "workgroup_name": "dpstack-workgroup",
        "database_name": "dpstack",
        "admin_username": "dpstack",
        "admin_password": "dpstack",
        "removal_policy": "DESTROY",
    },
    "batch": {
        "name": "dpstack-batch",
        "queue_name": "dpstack-batch-queue",
        "max_vcpus": 4,
        "min_vcpus": 0,
        "desired_vcpus": 0,
        "instance_types": ["optimal"],
        "removal_policy": "DESTROY",
    },
}
