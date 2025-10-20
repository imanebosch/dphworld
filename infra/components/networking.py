from aws_cdk import aws_ec2
from config import VPCConfig
from constructs import Construct


class Networking(Construct):
    def __init__(self, scope: Construct, construct_id: str, config: VPCConfig):
        super().__init__(scope, construct_id)

        subnet_configuration = [
            aws_ec2.SubnetConfiguration(
                name="Public subnet",
                subnet_type=aws_ec2.SubnetType.PUBLIC,
                cidr_mask=22,
            ),
            aws_ec2.SubnetConfiguration(
                name="Private isolated subnet 2",
                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=22,
            ),
        ]

        self.vpc = aws_ec2.Vpc(
            self,
            "VPC",
            max_azs=config.max_azs,
            nat_gateways=config.nat_gateways,
            subnet_configuration=subnet_configuration,
            cidr="172.16.0.0/16",
        )
