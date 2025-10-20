import json
from aws_cdk import (
    aws_redshiftserverless,
    aws_iam,
    aws_ec2,
    RemovalPolicy,
    aws_secretsmanager,
)
from constructs import Construct
from config import RedshiftConfig


class Warehouse(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        config: RedshiftConfig,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for Redshift Serverless
        self.redshift_role = aws_iam.Role(
            self,
            "RedshiftRole",
            assumed_by=aws_iam.ServicePrincipal("redshift.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonRedshiftAllCommandsFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
            ],
        )

        # Create security group for Redshift Serverless
        self.security_group = aws_ec2.SecurityGroup(
            self,
            "RedshiftSecurityGroup",
            vpc=vpc,
            description="Security group for Redshift Serverless",
            allow_all_outbound=True,
        )

        # Allow inbound connections on port 5439 (Redshift default port)
        self.security_group.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(5439),
            description="Allow Redshift connections from VPC",
        )

        # Create a secret for Redshift admin credentials
        self.admin_secret = aws_secretsmanager.Secret(
            self,
            "RedshiftAdminSecret",
            secret_name=f"{config.namespace_name}-admin-secret",
            description="Redshift Serverless admin credentials",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps(
                    {
                        "engine": "redshift",
                        "host": f"{config.workgroup_name}.{scope.account}.{scope.region}.redshift-serverless.amazonaws.com",
                        "port": 5439,
                        "username": config.admin_username,
                        "dbname": config.database_name,
                    }
                ),
                generate_string_key="password",
                password_length=16,
                exclude_characters="\"@/\\'",
                require_each_included_type=True,  # Requires uppercase, lowercase, numbers, symbols
            ),
        )

        # Grant the Redshift role permission to read the secret
        self.admin_secret.grant_read(self.redshift_role)

        # Create Redshift Serverless Namespace
        self.namespace = aws_redshiftserverless.CfnNamespace(
            self,
            "RedshiftNamespace",
            namespace_name=config.namespace_name,
            admin_username=config.admin_username,
            admin_user_password=self.admin_secret.secret_value_from_json(
                "password"
            ).unsafe_unwrap(),
            db_name=config.database_name,
            iam_roles=[self.redshift_role.role_arn],
        )

        # Create Redshift Serverless Workgroup
        self.workgroup = aws_redshiftserverless.CfnWorkgroup(
            self,
            "RedshiftWorkgroup",
            workgroup_name=config.workgroup_name,
            namespace_name=config.namespace_name,
            base_capacity=128,
            max_capacity=512,
            enhanced_vpc_routing=False,
            security_group_ids=[self.security_group.security_group_id],
            subnet_ids=[
                subnet.subnet_id for subnet in vpc.public_subnets
            ],  #: For local access (not ideal but avoid VPN)
            publicly_accessible=True,
        )

        self.workgroup.add_dependency(self.namespace)

        self.namespace.apply_removal_policy(RemovalPolicy[config.removal_policy])
        self.workgroup.apply_removal_policy(RemovalPolicy[config.removal_policy])
        self.admin_secret.apply_removal_policy(RemovalPolicy[config.removal_policy])
