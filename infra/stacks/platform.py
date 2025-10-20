from aws_cdk import Stack
from components.networking import Networking
from config import Config
from constructs import Construct
from components.compute import BatchCompute
from components.compute_jobs import ComputeJob
from components.wharehouse import Warehouse
from components.ecr import EcrRepository
from components.storage import Storage
from components.mwaa import Mwaa


class DataPlatform(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: Config,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.dbt_image = EcrRepository(self, "DbtImage", "dbt-image")
        self.ingestion_image = EcrRepository(self, "IgnestionImage", "ingestion-image")

        self.vpc_network = Networking(self, "VPC", config.vpc)
        self.storage = Storage(self, "Storage", config.storage)
        self.airflow = Mwaa(self, "Mwaa", self.vpc_network.vpc, config.mwaa)
        self.warehouse = Warehouse(
            self, "Warehouse", self.vpc_network.vpc, config.redshift
        )
        self.batch = BatchCompute(self, "Batch", self.vpc_network.vpc, config.batch)
        self.compute_job = ComputeJob(
            self,
            "ComputeJob",
            self.dbt_image.repository,
            self.ingestion_image.repository,
        )
