# Onboarding Guide – Scholarvalley Operating System

Welcome. This guide orients you to the project, how to run it, and where to find things. **Environment: macOS (MacBook).**

---

## What is this project?

- **Scholarvalley Operating System** – A backend API (FastAPI) plus a static frontend for the Scholarvalley product.
- **Purpose:** Applicants, documents, auth (JWT + roles), S3 uploads, Stripe payments, tasks, messages, eligibility checks, ML consent, audit logging. Designed to run on **AWS** (ECS, S3, RDS today; **DynamoDB / AWS-only** as target – see `docs/AWS_ONLY_ARCHITECTURE.md`).
- **Platform:** All instructions assume **macOS** (Terminal, zsh, Homebrew, Docker Desktop).

---

## Your first day

1. **Read**  
   - This file (ONBOARDING.md).  
   - High-level: **README.md** in the repo root.  
   - Full context: **docs/CODEBASE_CONTEXT.md**.

2. **Setup**  
   - Follow **docs/DEVELOPER_SETUP.md** (clone, `.env`, Docker, run app, migrations, seed).

3. **Run the app**  
   - `docker compose up --build`  
   - Open http://localhost:8000 and http://localhost:8000/docs.  
   - Log in with `root@localhost` / `root123` after seeding.

4. **Explore**  
   - **app/main.py** – app entry, routes, exception handler.  
   - **app/api/** – auth, applicants, documents, uploads, payments, tasks, messages, dashboard, eligibility, ml.  
   - **app/models/** – User, Applicant, Document, Task, Message, Payment, AuditLog, etc.  
   - **infra/** – Terraform for AWS.  
   - **docs/** – architecture, troubleshooting, changelog, prompt log.

---

## Key concepts

- **Auth:** JWT (access + refresh). Roles: **client**, **manager**, **root**. Root can do everything; clients see only their own data where applicable.
- **Database:** Currently **PostgreSQL** (local: Docker; AWS: RDS). Target direction: **AWS-only**, with **DynamoDB** as the data store (see AWS_ONLY_ARCHITECTURE.md).
- **Storage:** File uploads go to **S3** via presigned URLs.  
- **Secrets:** Local: `.env`. AWS: **Secrets Manager** (e.g. `DATABASE_URL`, `JWT_SECRET_KEY`).
- **Deploy:** Terraform in `infra/`; `./deploy.sh` for full deploy; scripts in `infra/` for secrets and prerequisites.

---

## Where to look when…

| You want to… | Look at… |
|--------------|----------|
| Understand the whole codebase | **docs/CODEBASE_CONTEXT.md** |
| Set up your machine | **docs/DEVELOPER_SETUP.md** |
| Fix an error | **docs/TROUBLESHOOTING.md** |
| See what changed over time | **docs/CHANGELOG.md** |
| Deploy to AWS | **infra/README.md**, **infra/DEPLOYMENT_GUIDE.md** |
| Understand AWS / DynamoDB direction | **docs/AWS_ONLY_ARCHITECTURE.md** |
| Understand AI/prompt context | **docs/PROMPT_LOG.md** |

---

## Conventions

- **macOS-first:** All commands and paths are for MacBook (Terminal, zsh, Homebrew, Docker Desktop).
- **Errors:** API returns JSON (including 500s); frontend uses `parseJson()` so non-JSON responses don’t break the client.
- **DB:** SQLModel + Alembic today; migration path to DynamoDB is documented in AWS_ONLY_ARCHITECTURE.md.

---

## Next steps

- Run the app and try the API from `/docs`.  
- Make a small change (e.g. add a field or endpoint) and run tests if the project has them.  
- Read **docs/AWS_ONLY_ARCHITECTURE.md** if you’ll work on infra or the move to DynamoDB.
