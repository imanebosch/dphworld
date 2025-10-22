# dpworld

A simple AWS-based data platform architecture designed for learning and practice.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Architecture Components](#architecture-components)
   - [Infrastructure (`/infra`)](#1-infrastructure-infra)
   - [Data Ingestion (`/ingestion`)](#2-data-ingestion-ingestion)
   - [Data Transformation (`/transformation_dbt`)](#3-data-transformation-transformation_dbt)
   - [Orchestration (`/orquestration`)](#4-orchestration-orquestration)
   - [CI/CD Pipeline (`.github/workflows/`)](#5-cicd-pipeline-githubworkflows)
3. [Setup Process](#setup-process)
   - [Prerequisites](#prerequisites)
   - [Environment Variables Setup](#1-environment-variables-setup)
   - [Deploy Infrastructure](#2-deploy-infrastructure)
   - [Upload Files to S3](#3-upload-files-to-s3)
   - [Configure GitHub Secrets](#4-configure-github-secrets)
   - [Trigger CI/CD Pipeline](#5-trigger-cicd-pipeline)
   - [Verify Deployment](#6-verify-deployment)
4. [Data Flow & Job Execution](#data-flow--job-execution)
   - [Data Flow Overview](#data-flow-overview)
   - [What Happens When Triggering a Job](#what-happens-when-triggering-a-job)

## Architecture Overview

This repository implements a modern data platform on AWS using Infrastructure as Code (CDK), containerized microservices, and automated CI/CD pipelines. 

## Architecture Components

### 1. Infrastructure (`/infra`)
**Purpose**: Defines and provisions AWS infrastructure using AWS CDK

**Key Components**:
- **VPC & Networking**: Multi-AZ VPC with NAT gateways for secure connectivity
- **Storage**: S3 data lake for raw and processed data storage
- **Compute**: AWS Batch for containerized data processing jobs
- **Data Warehouse**: Amazon Redshift Serverless for analytics
- **Orchestration**: Amazon MWAA (Managed Workflows for Apache Airflow)
- **Container Registry**: Amazon ECR for storing Docker images

**Configuration**: Environment-specific settings managed through Pydantic models in `/infra/settings/`

### 2. Data Ingestion (`/ingestion`)
**Purpose**: Extracts and loads data from external sources into the data lake

**Features**:
- Containerized Python applications for data extraction
- SpaceX API integration as example data source
- Configurable data sources and destinations
- Utility functions for common data operations

**Deployment**: Docker containers deployed to AWS Batch for scalable processing

### 3. Data Transformation (`/transformation_dbt`)
**Purpose**: Transforms raw data into analytics-ready datasets using dbt

**Features**:
- dbt project with standardized data models
- Data quality tests and documentation
- Incremental and full refresh capabilities
- Materialized views and tables in Redshift

**Deployment**: Containerized dbt runs executed via AWS Batch

### 4. Orchestration (`/orquestration`)
**Purpose**: Manages data pipeline workflows and scheduling with apache airflow

**Components**:
- **DAGs**: Apache Airflow workflows defining data pipeline steps
- **Scheduling**: Automated execution of ingestion and transformation jobs
- **Monitoring**: Pipeline health checks and failure handling

**Deployment**: DAGs deployed to Amazon MWAA via CI/CD pipeline

### 5. CI/CD Pipeline (`.github/workflows/`)
**Purpose**: Automated build and deployment of compute images and dags

**Pipeline Steps**:
1. **Build Phase**: 
   - Builds Docker images for ingestion and dbt services
   - Pushes images to Amazon ECR
2. **Deploy Phase**: 
   - Deploys DAGs to Amazon MWAA
   - Updates infrastructure via CDK

## Setup Process

### Prerequisites

Before setting up the data platform, ensure you have:

- Docker and Docker Compose installed
- Python 3.8+ installed
- Git
- boto3 python library (run `pip install -r requirments.txt`)

### 1. Environment Variables Setup

Create a `.env` file in the project root with the following variables:

```bash
# AWS Configuration
AWS_ACCOUNT_ID=your-aws-account-id
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=eu-west-1


# Settings Module (optional, defaults to 'dev')
SETTINGS_MODULE=dev

# Dbt
DBT_PROFILES_DIR=./

#: Development only
AIRFLOW_IMAGE_NAME=apache/airflow:3.1.0
AIRFLOW_PROJ_DIR=./orquestration
AIRFLOW_UID=1000
```

### 2. Deploy Infrastructure

#### Step 1: Deploy AWS Infrastructure
```bash
docker-compose run infra
```

### 2. Upload Files to S3

#### Upload DAGs to MWAA
```bash
python scripts/deploy_dags.py
```
This uploads Airflow DAGs from `orquestration/dags/` to the `dpstack-airflow` S3 bucket.

#### Upload Sample Data
```bash
python scripts/upload_file.py
```
This uploads sample SpaceX data to the `dpstack-dlake` S3 bucket.

### 4. Configure GitHub Secrets

Configure the following secrets in your GitHub repository:

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

**How to add secrets:**
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the corresponding name and value

### 5. Trigger CI/CD Pipeline

Make a commit to trigger the automated build and deployment:

```bash
# Make any change and commit
echo "# Trigger deployment" >> README.md
git add .
git commit -m "Trigger CI/CD pipeline"
git push origin main
```

**What happens automatically:**
1. **Build Phase**: 
   - Builds Docker images for ingestion and dbt services
   - Pushes images to Amazon ECR
2. **Deploy Phase**: 
   - Deploys DAGs to Amazon MWAA
   - Updates infrastructure via CDK

### 6. Verify Deployment

After deployment, you can verify the setup:

#### Check AWS Resources
- **S3 Buckets**: `dpstack-dlake`, `dpstack-airflow`
- **ECR Repositories**: `ingestion-image`, `dbt-image`
- **MWAA Environment**: `dpstack-airflow`
- **Redshift Workgroup**: `dpstack-workgroup`
- **Batch Queue**: `dpstack-batch-queue`

#### Access Airflow UI
1. Go to AWS MWAA console
2. Find the `dpstack-airflow` environment
3. Click "Open Airflow UI"
4. You should see the `ingestion` DAG available

## Data Flow & Job Execution

**Data Layers:**
1. **Raw Layer** (`s3://dpstack-dlake/raw/`): Unprocessed data from external sources
2. **Processed Layer** (`s3://dpstack-dlake/stage/`): Structured data
3. **Analytics Layer** (Redshift): Business-ready datasets and models in redshift

### What Happens When Triggering a Job

When you trigger the `ingestion` DAG in Airflow, here's the detailed execution flow:

#### 1. **DAG Trigger** 🚀
- User clicks "Trigger DAG" in Airflow UI
- Airflow scheduler picks up the DAG execution
- Creates a new DAG run with unique run ID

#### 2. **Task 1: Data Transformation** 📊
```python
# Task: transformation
# Job Definition: ingestion-job
# Command: python spacex/transformation.py
```

**What happens:**
- Airflow submits a job to AWS Batch queue `dpstack-batch-queue`
- AWS Batch pulls the `ingestion-image` from ECR
- Container starts with the transformation script
- Script fetches data from SpaceX API
- Processes and cleans the data
- Uploads processed data to S3 (`dpstack-dlake/processed/`)

#### 3. **Task 2: Data Copy** 📋
```python
# Task: copy_job  
# Job Definition: ingestion-job
# Command: python spacex/copy.py
```

**What happens:**
- Second AWS Batch job starts after transformation completes
- Uses the same container image but different script
- Copies processed data to Redshift staging area
- Validates data integrity and schema
- Updates data warehouse tables
