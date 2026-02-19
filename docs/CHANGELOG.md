# Changelog – Scholarvalley Operating System

All notable changes to the project are logged here. Format: newest first.

---

## [Unreleased]

- **Docs:** Developer setup guide – added step-by-step **Git configuration** (user.name, user.email, default branch, credential helper) for macOS.
- **Logs:** Rule: **all logs must be updated with new prompts.** On each new user prompt, update PROMPT_LOG.md (add prompt), CHANGELOG.md (if changes or doc updates), and any other project logs. See PROMPT_LOG.md "How to use this log" and persistent constraints.
- **Docs:** Added `docs/CODEBASE_CONTEXT.md`, `docs/CHANGELOG.md`, `docs/TROUBLESHOOTING.md`, `docs/DEVELOPER_SETUP.md`, `docs/ONBOARDING.md`, `docs/PROMPT_LOG.md`, `docs/AWS_ONLY_ARCHITECTURE.md`.
- **Architecture direction:** Documented AWS-only preference; database target DynamoDB (see `AWS_ONLY_ARCHITECTURE.md`). Current implementation still uses RDS PostgreSQL.

---

## 2025-02 (summary of prior work)

### Infra & AWS

- **Terraform:** Added Secrets Manager secret; ECS task definition injects `DATABASE_URL` and `JWT_SECRET_KEY` from Secrets Manager. IAM execution role granted `secretsmanager:GetSecretValue` for app secret.
- **Scripts:** Added `infra/deploy.sh` (full deploy), `infra/update-secrets.sh` (Secrets Manager), `infra/setup-prerequisites.sh` (Homebrew/AWS CLI/Terraform check). Fixed deploy.sh password prompt and summary (Secrets Manager name).
- **Outputs:** Terraform outputs for `cluster_name`, `service_name`, `secrets_manager_secret_arn`, `secrets_manager_secret_name`.
- **Docs:** `infra/README.md` – macOS note, prerequisite install links. `infra/DEPLOYMENT_GUIDE.md` – step-by-step deploy. Main `README.md` – "On macOS (MacBook)" section.

### Application

- **Config:** `app/core/config.py` – required `JWT_SECRET_KEY`, `AWS_S3_BUCKET`; `extra="ignore"`; optional `alembic_db_url`, `app_secret`; `database_url` validator normalizes to `postgresql+psycopg2://`.
- **Audit:** Renamed `AuditLog.metadata` to `extra_data` (SQLAlchemy reserved). Audit `log_event` receives DB session via `Depends(get_session)` in uploads.
- **Dashboard:** Fixed revenue query – added `select_from(Payment)`.
- **Eligibility:** Pydantic v2 – `payload.dict()` → `payload.model_dump()`.
- **Auth/email:** Replaced `EmailStr` with `str` + validators to avoid `email-validator` dependency.
- **Frontend:** `parseJson(r)` in login.js, dashboard.js, register.js (response.text then JSON.parse); global exception handler returns JSON for 500s; user-friendly DB error messages.

### Git & repo

- **Git:** Initialized repo; `.gitignore` (Python, .env, Terraform state, IDE, etc.). Initial commit with 70 files. Second commit: infra deploy script, Secrets Manager, deployment guide, setup script.
- **README:** macOS-specific notes; activate command labeled "macOS/Linux" vs Windows.

---

## Earlier (pre–changelog)

- FastAPI backend: auth (JWT, RBAC), applicants, documents (S3 bundles), uploads (presigned), payments (Stripe), tasks, messages, dashboard, eligibility, ML consent stub, audit logging.
- SQLModel models and Alembic migrations; Docker and docker-compose (api + Postgres).
- Static frontend (Scholarvalley branding, register, login, dashboard); root user seed script.
- Terraform: S3, ECR, RDS, ECS Fargate, ALB, IAM, security groups; GitHub Actions workflow for ECR build/push.
- `docs/AWS_ARCHITECTURE.md` – component mapping to AWS services.
