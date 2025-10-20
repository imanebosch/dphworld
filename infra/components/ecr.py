from aws_cdk import RemovalPolicy
from aws_cdk import aws_ecr
from constructs import Construct


class EcrRepository(Construct):
    def __init__(self, scope: Construct, construct_id: str, name: str):
        super().__init__(scope, construct_id)

        self.repository = aws_ecr.Repository(
            self,
            "Repository",
            repository_name=name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )
