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
.github/workflows/       - CI/CD workflows
environments/            - Env-specific configs (dev, staging, prod)
modules/                 - Terraform modules (api, auth, compute, database, storage, vpc)
rag_ui/                  - Streamlit frontend
scripts/                 - Utility scripts (cleanup, imports, diagnostics)
src/                     - Backend Lambda code
```

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
