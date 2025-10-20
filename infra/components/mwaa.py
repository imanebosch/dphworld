from aws_cdk import (
    RemovalPolicy,
    aws_mwaa,
    aws_ec2,
    aws_iam,
    aws_s3,
    Aws,
)
from constructs import Construct
from config import MwaaConfig


class Mwaa(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        config: MwaaConfig,
    ):
        super().__init__(scope, construct_id)

        # Create S3 bucket for MWAA DAGs and requirements
        self.dags_bucket = aws_s3.Bucket(
            self,
            "MwaaBucket",
            bucket_name=config.bucket_name,
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy[config.removal_policy],
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True,
        )

        # Create IAM role for MWAA
        self.mwaa_role = aws_iam.Role(
            self,
            "MWAARole",
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("airflow-env.amazonaws.com"),
                aws_iam.ServicePrincipal("airflow.amazonaws.com"),
            ),
        )

        # Add airflow metrics permission
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["airflow:PublishMetrics"],
                resources=[
                    f"arn:aws:airflow:{Aws.REGION}:{Aws.ACCOUNT_ID}:environment/{config.name}"
                ],
            )
        )

        # Add S3 deny policy for ListAllMyBuckets
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "batch:SubmitJob",
                    "batch:DescribeJobs",
                    "batch:DescribeJobQueues",
                    "batch:DescribeJobDefinitions",
                    "batch:ListJobs",
                    "batch:TerminateJob",
                    "batch:CancelJob",
                ],
                resources=["*"],
            )
        )

        # Add inline policy for S3 access
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "s3:ListAllMyBuckets",
                    "s3:GetObject*",
                    "s3:GetBucketVersioning",
                    "s3:List*",
                    "s3:GetBucket*",
                    "s3:GetBucketPublicAccessBlock",
                ],
                resources=[
                    self.dags_bucket.bucket_arn,
                    f"{self.dags_bucket.bucket_arn}/*",
                ],
            )
        )

        # Add separate policy for account-level S3 permissions
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "s3:GetAccountPublicAccessBlock",
                ],
                resources=["*"],  # This permission requires account-level access
            )
        )

        # Add inline policy for CloudWatch Logs
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:CreateLogGroup",
                    "logs:PutLogEvents",
                    "logs:GetLogEvents",
                    "logs:GetLogRecord",
                    "logs:GetLogGroupFields",
                    "logs:GetQueryResults",
                    "logs:DescribeLogGroups",
                ],
                resources=[
                    f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:*",
                ],
            )
        )

        # Add inline policy for CloudWatch Logs
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "logs:DescribeLogGroups",
                ],
                resources=["*"],
            )
        )

        # Add SQS permissions for Celery
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "sqs:ChangeMessageVisibility",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:GetQueueUrl",
                    "sqs:ReceiveMessage",
                    "sqs:SendMessage",
                ],
                resources=[f"arn:aws:sqs:{Aws.REGION}:*:airflow-celery-*"],
            )
        )

        # Add inline policy for CloudWatch metrics
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData",
                ],
                resources=["*"],
            )
        )

        # Add inline policy for KMS
        self.mwaa_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "kms:Decrypt",
                    "kms:DescribeKey",
                    "kms:GenerateDataKey*",
                    "kms:Encrypt",
                ],
                not_resources=[f"arn:aws:kms:*:{Aws.ACCOUNT_ID}:key/*"],
                conditions={
                    "StringLike": {"kms:ViaService": f"sqs.{Aws.REGION}.amazonaws.com"}
                },
            )
        )

        # Create security group for MWAA
        self.security_group = aws_ec2.SecurityGroup(
            self,
            "MWAASecurityGroup",
            vpc=vpc,
            description="Security group for MWAA environment",
            allow_all_outbound=True,
        )

        aws_ec2.CfnSecurityGroupIngress(
            self,
            "SecurityGroupSelfReference",
            group_id=self.security_group.security_group_id,
            ip_protocol="-1",
            source_security_group_id=self.security_group.security_group_id,
        )

        # Create MWAA environment
        self.environment = aws_mwaa.CfnEnvironment(
            self,
            "MWAAEnvironment",
            name=config.name,
            airflow_version="3.0.6",
            dag_s3_path="dags",
            environment_class="mw1.small",
            execution_role_arn=self.mwaa_role.role_arn,
            logging_configuration=aws_mwaa.CfnEnvironment.LoggingConfigurationProperty(
                dag_processing_logs=aws_mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO",
                ),
                scheduler_logs=aws_mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO",
                ),
                task_logs=aws_mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO",
                ),
                webserver_logs=aws_mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO",
                ),
                worker_logs=aws_mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO",
                ),
            ),
            max_workers=10,
            min_workers=1,
            network_configuration=aws_mwaa.CfnEnvironment.NetworkConfigurationProperty(
                security_group_ids=[self.security_group.security_group_id],
                subnet_ids=[
                    subnet.subnet_id
                    for i, subnet in enumerate(vpc.private_subnets)
                    if i < 2
                ],
            ),
            source_bucket_arn=self.dags_bucket.bucket_arn,
            webserver_access_mode="PUBLIC_ONLY",
        )

        # Add dependency to ensure the role is created before the environment
        self.environment.add_dependency(self.mwaa_role.node.default_child)
