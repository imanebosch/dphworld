from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_eks,
    aws_ec2,
    aws_rds,
    aws_secretsmanager,
)
from constructs import Construct
from config import AirflowConfig


class Airflow(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        eks: aws_eks.Cluster,
        config: AirflowConfig,
    ):
        super().__init__(scope, construct_id)

        self.subnet_group = aws_ec2.SubnetGroup(
            self,
            "RDSSubnetGroup",
            vpc=vpc,
            description="Subnet group for Airflow RDS database",
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )

        self.security_group = aws_ec2.SecurityGroup(
            self,
            "RDSSecurityGroup",
            vpc=vpc,
            description="Security group for Airflow RDS database",
            allow_all_outbound=True,
        )

        # Create secret for database credentials
        self.secret = aws_secretsmanager.Secret(
            self,
            "AirflowDBSecret",
            description="Airflow database credentials",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "airflow"}',
                generate_string_key="password",
                exclude_characters='"@/\\',
            ),
        )

        #: Airflow Database (RDS)
        self.database = aws_rds.DatabaseInstance(
            self,
            "AirflowDatabase",
            engine=aws_rds.DatabaseInstanceEngine.postgres(
                version=aws_rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=aws_ec2.InstanceType(config.rds.instance_type),
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.security_group],
            subnet_group=self.subnet_group,
            database_name="airflow",
            credentials=aws_rds.Credentials.from_secret(self.secret),
            backup_retention=Duration.days(config.rds.backup_retention_days),
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,
            storage_encrypted=True,
            multi_az=False,
        )
