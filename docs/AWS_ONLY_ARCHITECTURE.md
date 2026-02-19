# AWS-Only Architecture – Scholarvalley

**User requirement:** Use **only AWS services**. For the database, use **DynamoDB** or another AWS service (no non-AWS or self-managed DB).

This document describes the **target** architecture and the **current** state. The codebase today still uses **Amazon RDS (PostgreSQL)**; the migration path to **DynamoDB** (or another AWS-native store) is outlined below.

---

## Target: 100% AWS services

| Need | AWS service | Notes |
|------|-------------|--------|
| **Compute** | ECS Fargate (or Lambda) | Already in use (Fargate). |
| **Database** | **DynamoDB** (or Aurora Serverless v2, DocumentDB) | **Target:** DynamoDB for primary app data. Alternative: Aurora Serverless v2 if SQL is required. |
| **File storage** | S3 | Already in use. |
| **Secrets** | Secrets Manager (or SSM Parameter Store) | Already in use. |
| **Email** | SES | Already in use. |
| **Container registry** | ECR | Already in use. |
| **Load balancing** | ALB (+ ACM for HTTPS) | Already in use. |
| **Logs / metrics** | CloudWatch Logs, CloudWatch Metrics | ECS already sends logs. |
| **CI/CD** | GitHub Actions → ECR; Terraform apply (or CodePipeline/CodeBuild) | Already in use. |
| **Payments** | Stripe (external) | No AWS equivalent; remains external. |

**Database choice (user preference):** **DynamoDB** or an AWS service. So:

- **Option A – DynamoDB:** Primary data store for users, applicants, documents, tasks, messages, payments, audit, etc. No RDS.
- **Option B – Aurora Serverless v2 (PostgreSQL):** Keeps SQL and minimal app changes; still 100% AWS.
- **Option C – DocumentDB:** If document-style data is preferred but with MongoDB-compatible API.

This project’s **stated preference** is **DynamoDB** (or “an AWS service” for DB). Below we outline Option A.

---

## Current state vs target

| Component | Current | Target (AWS-only) |
|-----------|---------|-------------------|
| Database | RDS PostgreSQL | **DynamoDB** (tables per entity or single-table design) |
| App data layer | SQLModel, SQLAlchemy, psycopg2, Alembic | boto3 DynamoDB client; no SQL migrations |
| Secrets | Secrets Manager | Same |
| Compute / storage / etc. | ECS, S3, ECR, ALB | Same |

---

## What changes for DynamoDB

1. **Terraform**
   - Remove RDS (and RDS security group, subnet group).
   - Add DynamoDB tables (e.g. `users`, `applicants`, `documents`, `tasks`, `messages`, `payments`, `audit_log`, etc.) with appropriate keys (partition key, optional sort key) and GSIs as needed.
   - ECS task env: no `DATABASE_URL`; instead table names or ARNs via env or SSM.

2. **Application**
   - Replace SQLModel/SQLAlchemy with **boto3** DynamoDB (e.g. `get_item`, `put_item`, `query`, `scan` with filters).
   - Replace Alembic migrations with DynamoDB table creation/updates in Terraform (or a one-off script). No SQL.
   - Models become Pydantic/Dict representations; IDs (e.g. UUID) as partition keys; design GSIs for “list by owner”, “list by status”, etc.
   - Session/dependency: inject a DynamoDB client or table resource instead of `get_session()`.

3. **Secrets Manager**
   - No `DATABASE_URL`. Optionally store table names or other config if not in env.
   - Keep `JWT_SECRET_KEY` and other app secrets as today.

4. **Local development**
   - Option A: DynamoDB Local in Docker; point app to local endpoint.  
   - Option B: Use real DynamoDB tables in a dev AWS account.  
   - docker-compose can run DynamoDB Local instead of Postgres for full AWS-only local stack.

---

## Implementation order (suggested)

1. **Document and agree** on DynamoDB table design (keys, GSIs) for users, applicants, documents, tasks, messages, payments, audit.
2. **Terraform:** Add DynamoDB tables; remove RDS and related resources; update ECS task env (table names).
3. **App:** Introduce a small **DynamoDB data layer** (e.g. `app/db/dynamodb.py` or `app/repositories/`) and migrate one domain at a time (e.g. auth/users first, then applicants, then documents, etc.).
4. **Remove** SQLModel models, Alembic, and `DATABASE_URL` from config once migration is complete.
5. **Update** developer setup, onboarding, and troubleshooting docs to describe DynamoDB (and DynamoDB Local if used).

---

## References

- **Context and conventions:** `docs/CODEBASE_CONTEXT.md`
- **Prompt log (incl. AWS-only / DynamoDB preference):** `docs/PROMPT_LOG.md`
- **Current AWS layout (RDS):** `docs/AWS_ARCHITECTURE.md`
- **Terraform (current):** `infra/main.tf` (RDS, ECS, S3, ECR, ALB, Secrets Manager)

All future changes should respect: **AWS-only**, **DynamoDB (or AWS DB) for database**, and **macOS** as the development environment, unless a later prompt in **PROMPT_LOG.md** explicitly overrides this.
