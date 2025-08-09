# End-to-End RAG Application with Evaluation on AWS

Terraform-based **Infrastructure as Code (IaC)** to deploy a complete AWS backend for a Retrieval-Augmented Generation (RAG) application. It integrates with Google’s free-tier Gemini Pro and Embedding models for AI-powered document querying and includes a Streamlit UI with token-based authentication for interacting with the app.

💰 **Estimated cost**: ~$3 (~₹250) to experiment without the AWS Free Tier, primarily for RDS and NAT Gateway if active.

👉 **Related UI**: [RAG UI (Streamlit Frontend)](https://github.com/genieincodebottle/rag-app-on-aws/tree/main/rag_ui) — A Streamlit-based frontend application designed to interact with the backend infrastructure deployed by this project.

---

## 🔍 Overview

This repository contains the complete Terraform codebase for provisioning and managing the AWS infrastructure that powers a RAG application. It allows users to upload documents, which are processed, embedded, and stored for efficient semantic search and AI-driven querying.

**Key features include:**
- **IaC with Terraform** for consistent deployments.
- **Serverless Compute** using AWS Lambda for backend logic.
- **Vector Storage** with PostgreSQL RDS and `pgvector`.
- **AI Integration** with Google’s Gemini Pro and Embedding models.
- **Authentication** via AWS Cognito.
- **CI/CD Workflows** using GitHub Actions.
- **Multi-Environment Support** (`dev`, `staging`, `production`).
- **Comprehensive Testing** for backend Lambdas.
- **Streamlit UI** for document upload, querying, and evaluation.

---

## 🌐 Network Flow Walkthrough

**Document Processing Flow**
1. User uploads document → API Gateway → `upload_handler` Lambda.
2. Lambda stores file in S3.
3. S3 triggers `document_processor` Lambda.
4. Processor generates embeddings using Gemini API.
5. Stores embeddings and metadata in PostgreSQL RDS.

**Query Processing Flow**
1. User query → API Gateway → `query_processor` Lambda.
2. Lambda performs vector similarity search in PostgreSQL.
3. Retrieves relevant chunks and context.
4. Uses Gemini Pro to generate answer.
5. Returns result to user.

---

## 🗂 Repository Structure
```
.
├── .github/workflows/       # CI/CD via GitHub Actions
│   ├── deploy.yml           # Infrastructure deployment workflow
│   └── manual_cleanup.yml   # Resource cleanup workflow
├── environments/            # Environment-specific configs (dev, staging, prod)
│   └── dev/                 # Example 'dev' environment
│       ├── main.tf          # Root Terraform file for the environment
│       ├── providers.tf     # Terraform provider configurations
│       └── variables.tf     # Environment-specific variable definitions
├── modules/                 # Reusable Terraform modules
│   ├── api/                 # API Gateway configuration
│   ├── auth/                # Cognito authentication
│   ├── compute/             # Lambda functions & IAM roles
│   ├── database/            # PostgreSQL RDS with pgvector & Secrets Manager
│   ├── monitoring/          # CloudWatch Logs, Alarms & SNS Topic
│   ├── storage/             # S3 Buckets & DynamoDB Table
│   └── vpc/                 # VPC, Subnets, NAT, Security Groups, Endpoints
├── rag_ui/                  # Streamlit UI application
│   ├── app.py               # Main Streamlit application code
│   └── README.md            # README specific to the UI
├── scripts/                 # Utility shell scripts
│   ├── cleanup.sh           # Comprehensive resource cleanup script
│   ├── import_resources.sh  # Script to import existing AWS resources into Terraform state
│   └── network-diagnostics.sh # Script for troubleshooting network connectivity (e.g., Lambda to RDS)
├── src/                     # Lambda backend source code (Python)
│   ├── auth_handler/        # Lambda for Cognito authentication operations
│   ├── db_init/             # Lambda for database schema and pgvector initialization
│   ├── document_processor/  # Lambda for processing uploaded documents
│   ├── query_processor/     # Lambda for handling user queries and RAG
│   ├── tests/               # Unit and integration tests
│   │   ├── integration/     # Integration tests for deployed services
│   │   │   └── run_integration_tests.py
│   │   ├── unit/            # Unit tests for Lambda functions
│   │   │   ├── conftest.py  # Pytest common fixtures and mocks
│   │   │   ├── test_*.py    # Individual unit test files
│   │   └── __init__.py
│   ├── upload_handler/      # Lambda for handling file uploads via API
│   └── utils/               # Shared utility code (e.g., db_connectivity_test.py)
├── sonar-project.properties # SonarQube configuration file
└── tox.ini                  # tox configuration for running tests and linters

---

## 🧱 Infrastructure Components

**1. Networking (VPC)**
- Custom VPC with public, private, and DB subnets.
- NAT & Internet Gateways.
- Security Groups and VPC Endpoints.
- Optional VPC Flow Logs.

**2. Compute (Lambda Functions)**
- Authentication (`auth_handler`).
- Document Processing (`document_processor`).
- Query Handling (`query_processor`).
- File Upload (`upload_handler`).
- Database Initialization (`db_init`).

**3. Storage**
- S3 Buckets for documents, Lambda packages, and Terraform state.
- DynamoDB for document metadata and Terraform locks.
- PostgreSQL RDS with `pgvector`.

**4. API & Authentication**
- API Gateway routes: `/upload`, `/query`, `/auth`.
- Cognito for user management.
- JWT-based API Authorization.
- AWS Secrets Manager for credentials.

**5. Monitoring & Alerts**
- CloudWatch Logs & Alarms.
- SNS notifications for alerts.

---

## ⚙️ Build and Deployment

**Prerequisites**
- Python 3.11+
- AWS Account
- GitHub Account
- Git installed locally
- Google API Key for Gemini models
- (Optional) SonarCloud account for code quality checks

**Deployment Steps**
1. Fork this repo.
2. Clone locally.
3. Update `terraform.tfvars` for your environment.
4. Add required GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - (Optional) `SONAR_TOKEN`
5. Trigger GitHub Actions pipeline to deploy.

---

## 🌍 Environment Management
Supports multiple environments (`dev`, `staging`, `prod`) with separate configurations in `environments/`.

---

## 🚀 Running the Streamlit UI
1. Deploy AWS resources.
2. Navigate to `rag_ui/`.
3. Create a Python virtual environment and install dependencies.
4. Configure `.env` file with API endpoint and Cognito client ID.
5. Run `streamlit run app.py` and access UI locally.

---

## 🧰 Utilities
- `cleanup.sh` — remove all AWS resources for an environment.
- `import_resources.sh` — import existing resources into Terraform.
- `network-diagnostics.sh` — troubleshoot VPC and DB connectivity.

---

## 🧹 Uninstallation
Use GitHub Actions **Manual AWS Cleanup** workflow or run `cleanup.sh` to remove all resources for a specific environment.
