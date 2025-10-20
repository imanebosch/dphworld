from aws_cdk import (
    aws_batch,
    aws_ecr,
    aws_iam,
)
from constructs import Construct


class ComputeJob(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        dbt_image: aws_ecr.Repository,
        ingestion_image: aws_ecr.Repository,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Task Execution Role - for ECS task execution
        self.task_execution_role = aws_iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMReadOnlyAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBatchServiceRole"
                ),
            ],
        )

        # Add custom policies for task execution role
        self.task_execution_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "batch:SubmitJob",
                    "batch:DescribeJobs",
                ],
                resources=["*"],
            )
        )

        self.task_execution_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "kms:Decrypt",
                    "secretsmanager:GetSecretValue",
                    "ssm:GetParameters",
                ],
                resources=["*"],
            )
        )

        # Batch Container IAM Role - for the container itself
        self.batch_container_role = aws_iam.Role(
            self,
            "BatchContainerIAMRole",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMReadOnlyAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonRedshiftFullAccess"
                ),
            ],
        )

        self.batch_container_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameters",
                    "secretsmanager:GetSecretValue",
                    "kms:Decrypt",
                    "batch:SubmitJob",
                    "sts:AssumeRole",
                    "redshift-serverless:*",  #: TODO Limit to specific actions
                ],
                resources=["*"],
            )
        )

        # Job Definition for DBT Transformation
        self.dbt_job_definition = aws_batch.CfnJobDefinition(
            self,
            "DbtJobDefinition",
            job_definition_name="dbt-transformation-job",
            type="container",
            retry_strategy=aws_batch.CfnJobDefinition.RetryStrategyProperty(attempts=1),
            platform_capabilities=["FARGATE"],
            container_properties=aws_batch.CfnJobDefinition.ContainerPropertiesProperty(
                environment=[
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_PROFILES_DIR", value="./"
                    ),
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_TARGET_PATH", value="dbt/target"
                    ),
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_LOG_PATH", value="dbt/logs"
                    ),
                ],
                job_role_arn=self.batch_container_role.role_arn,
                execution_role_arn=self.task_execution_role.role_arn,
                command=["echo", "test"],
                image=f"{dbt_image.repository_uri}:latest",
                resource_requirements=[
                    aws_batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="MEMORY", value="2048"
                    ),
                    aws_batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="VCPU", value="1"
                    ),
                ],
            ),
        )

        # Job Definition for DBT Transformation
        self.ingestion_job_definition = aws_batch.CfnJobDefinition(
            self,
            "IgnestionJobDefinition",
            job_definition_name="ingestion-job",
            type="container",
            retry_strategy=aws_batch.CfnJobDefinition.RetryStrategyProperty(attempts=1),
            platform_capabilities=["FARGATE"],
            container_properties=aws_batch.CfnJobDefinition.ContainerPropertiesProperty(
                environment=[
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_PROFILES_DIR", value="./"
                    ),
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_TARGET_PATH", value="dbt/target"
                    ),
                    aws_batch.CfnJobDefinition.EnvironmentProperty(
                        name="DBT_LOG_PATH", value="dbt/logs"
                    ),
                ],
                job_role_arn=self.batch_container_role.role_arn,
                execution_role_arn=self.task_execution_role.role_arn,
                command=["echo", "test"],
                image=f"{ingestion_image.repository_uri}:latest",
                resource_requirements=[
                    aws_batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="MEMORY", value="2048"
                    ),
                    aws_batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="VCPU", value="1"
                    ),
                ],
            ),
        )
