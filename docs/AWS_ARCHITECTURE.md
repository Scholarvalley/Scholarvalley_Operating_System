# Scholarvalley on AWS – Architecture

Everything in Scholarvalley is designed to run on AWS. This document maps each component to AWS services and how they connect.

## High-level mapping

| Component | AWS service | Notes |
|-----------|-------------|--------|
| **Compute** | ECS Fargate | FastAPI runs in a container; no servers to manage. Alternative: Lambda + Mangum for serverless. |
| **Database** | Amazon RDS (PostgreSQL) or Aurora PostgreSQL | `DATABASE_URL` from Secrets Manager or SSM. |
| **File storage** | Amazon S3 | Presigned uploads; documents and static assets. Use SSE-KMS. |
| **Email** | Amazon SES | Transactional email (verification, notifications). Verify domain/sender. |
| **Secrets & config** | AWS Secrets Manager or SSM Parameter Store | `DATABASE_URL`, `JWT_SECRET_KEY`, Stripe keys, etc. |
| **Container registry** | Amazon ECR | Docker image for the FastAPI app. |
| **Load balancing & TLS** | Application Load Balancer (ALB) + ACM | HTTPS termination; health checks to ECS. |
| **DNS** | Route 53 | Optional; point your domain to the ALB. |
| **CDN / static** | CloudFront | Optional; put in front of ALB and/or S3 for static assets. |
| **Networking** | VPC, public/private subnets | ECS in private subnets; ALB in public. RDS in private subnets. |
| **IAM** | IAM roles for ECS task, Lambda, etc. | Least privilege: S3, SES, Secrets Manager, RDS (via security group). |
| **Logs & metrics** | CloudWatch Logs, CloudWatch Metrics | ECS sends logs to CloudWatch; optional alarms. |
| **CI/CD** | GitHub Actions → ECR, Terraform (or CodePipeline) | Build image, push to ECR, deploy via Terraform apply or ECS update. |
| **Payments** | Stripe (external) | Webhook receives events; no AWS service for payments. |
| **ML (future)** | SageMaker, or external Deepseek API | Training data in S3; consent in RDS. |

## Data flow

1. **User → ALB → ECS (FastAPI)** over HTTPS.
2. **FastAPI** reads config from **env vars** (injected from Secrets Manager/SSM by ECS task definition).
3. **FastAPI** connects to **RDS** via `DATABASE_URL` (private subnet, security group).
4. **Uploads**: FastAPI generates presigned S3 URLs; client uploads directly to **S3**. Optional: S3 event → Lambda (e.g. virus scan) → update DB.
5. **Email**: FastAPI uses **boto3** to call **SES** (same region).
6. **Stripe**: Client pays via Stripe; Stripe sends webhook to **ALB → ECS**; FastAPI validates signature and updates **RDS**.

## Required IAM permissions (ECS task role)

The role assumed by the ECS task (or Lambda) should allow:

- **S3**: `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`, `s3:GeneratePresignedUrl` (or use bucket policy + IAM).
- **SES**: `ses:SendEmail`, `ses:SendRawEmail`.
- **Secrets Manager** (if fetching secrets at runtime): `secretsmanager:GetSecretValue` for the app secret.
- **CloudWatch Logs**: `logs:CreateLogStream`, `logs:PutLogEvents` (if using awslogs log driver).

RDS access is via **network + security group** (no IAM for DB auth unless using IAM auth for PostgreSQL).

## Environment variables on AWS

Set these in the ECS task definition (from Secrets Manager or SSM, or plain env):

| Variable | Source on AWS |
|----------|----------------|
| `DATABASE_URL` | Secrets Manager secret or SSM (secure). Format: `postgresql+psycopg2://user:pass@rds-endpoint:5432/dbname` |
| `JWT_SECRET_KEY` | Secrets Manager |
| `JWT_ALGORITHM` | Plain env, e.g. `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Plain env |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Plain env |
| `AWS_REGION` | Plain env, e.g. `us-east-1` |
| `AWS_S3_BUCKET` | Plain env or SSM; bucket created by Terraform |
| `STRIPE_SECRET_KEY` | Secrets Manager |
| `STRIPE_WEBHOOK_SECRET` | Secrets Manager |
| `SES_FROM_EMAIL` | Plain env; must be verified in SES |
| `FRONTEND_ORIGIN` | Plain env; your frontend URL for CORS |

## Terraform and CI/CD

- **`infra/`** – Terraform to create VPC (optional), RDS, S3, ECR, ECS Fargate, ALB, IAM, and optionally Secrets Manager placeholders.
- **`.github/workflows/deploy.yml`** – Builds the Docker image, pushes to ECR, and can run `terraform apply` (or trigger CodePipeline) for deployment.

See `infra/README.md` for how to run Terraform and deploy.
