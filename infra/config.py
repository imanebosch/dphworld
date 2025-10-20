import importlib
import os
from pydantic import BaseModel


class VPCConfig(BaseModel):
    max_azs: int
    nat_gateways: int


class StorageConfig(BaseModel):
    name: str
    removal_policy: str


class MwaaConfig(BaseModel):
    name: str
    bucket_name: str
    removal_policy: str


class RedshiftConfig(BaseModel):
    namespace_name: str
    workgroup_name: str
    database_name: str
    admin_username: str
    admin_password: str
    removal_policy: str


class BatchConfig(BaseModel):
    name: str
    queue_name: str
    max_vcpus: int
    min_vcpus: int
    desired_vcpus: int
    instance_types: list[str]
    removal_policy: str


class Config(BaseModel):
    region: str
    account: str
    name: str
    vpc: VPCConfig
    storage: StorageConfig
    mwaa: MwaaConfig
    redshift: RedshiftConfig
    batch: BatchConfig


settings_module = importlib.import_module(
    "settings." + os.getenv("SETTINGS_MODULE", "dev")
)
settings = Config(**settings_module.config)
