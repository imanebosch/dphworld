from aws_cdk import (
    aws_batch,
    aws_ec2,
    aws_iam,
    RemovalPolicy,
)
from config import BatchConfig
from constructs import Construct


class BatchCompute(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        config: BatchConfig,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for AWS Batch service
        self.batch_service_role = aws_iam.Role(
            self,
            "BatchServiceRole",
            assumed_by=aws_iam.ServicePrincipal("batch.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBatchServiceRole"
                )
            ],
        )

        # Create IAM role for Batch instances
        self.batch_instance_role = aws_iam.Role(
            self,
            "BatchInstanceRole",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonEC2ContainerServiceforEC2Role"
                )
            ],
        )

        # Create security group for ECS hosts
        self.ecs_host_security_group = aws_ec2.SecurityGroup(
            self,
            "EcsHostSecurityGroup",
            vpc=vpc,
            description="Access to the ECS hosts that run containers",
        )

        # Allow ingress from other containers in the same security group
        self.ecs_host_security_group.add_ingress_rule(
            peer=self.ecs_host_security_group,
            connection=aws_ec2.Port.all_traffic(),
            description="Ingress from other containers in the same security group",
        )

        # Create Batch compute environment
        self.compute_environment = aws_batch.CfnComputeEnvironment(
            self,
            "BatchComputeEnvironment",
            type="MANAGED",
            service_role=self.batch_service_role.role_arn,
            compute_resources=aws_batch.CfnComputeEnvironment.ComputeResourcesProperty(
                type="FARGATE",
                maxv_cpus=config.max_vcpus,
                security_group_ids=[self.ecs_host_security_group.security_group_id],
                subnets=[subnet.subnet_id for subnet in vpc.private_subnets],
            ),
            state="ENABLED",
        )

        # Create Batch job queue
        self.job_queue = aws_batch.CfnJobQueue(
            self,
            "BatchJobQueue",
            job_queue_name=config.queue_name,
            compute_environment_order=[
                aws_batch.CfnJobQueue.ComputeEnvironmentOrderProperty(
                    compute_environment=self.compute_environment.ref,
                    order=1,
                )
            ],
            priority=1,
            state="ENABLED",
        )

        # Apply removal policy
        self.compute_environment.apply_removal_policy(
            RemovalPolicy[config.removal_policy]
        )
        self.job_queue.apply_removal_policy(RemovalPolicy[config.removal_policy])
