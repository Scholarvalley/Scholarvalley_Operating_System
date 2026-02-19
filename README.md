# Scholarvalley Operating System – Backend

Backend service for Scholarvalley, built with **FastAPI** and designed to run fully on **AWS**: RDS, S3, SES, ECS Fargate, ECR, ALB. It includes JWT auth, S3 presigned uploads, Stripe, tasks, messages, eligibility, ML consent, and audit logging.

## Tech stack

- **Language**: Python 3.11+
- **Web framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy-based)
- **DB**: PostgreSQL (locally via Docker or direct; in cloud via Amazon RDS/Aurora)
- **Storage**: Amazon S3 (presigned URLs)
- **Auth**: JWT (access/refresh), RBAC (client / manager / root)
- **Email**: Amazon SES
- **Payments**: Stripe (checkout sessions + webhooks)
- **Containerization**: Docker, ready for ECS/Fargate

## On macOS (MacBook)

All instructions in this repo are written for **macOS**. You can run them in Terminal (zsh). Notes:

- **Homebrew** for AWS CLI / Terraform: `brew install awscli terraform` (install Homebrew first if needed).
- **Docker**: use [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop); start it before `docker compose` or `docker build`.
- **Paths**: use `/Users/...` paths and forward slashes; no `\` or `C:\`.
- **Apple Silicon (M1/M2/M3)**: everything works; no extra steps.

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/CODEBASE_CONTEXT.md](docs/CODEBASE_CONTEXT.md) | Full codebase context and structure |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Log of all changes |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Troubleshooting guide |
| [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) | Developer setup (macOS) |
| [docs/ONBOARDING.md](docs/ONBOARDING.md) | Onboarding guide |
| [docs/PROMPT_LOG.md](docs/PROMPT_LOG.md) | Prompt log (updated on each new prompt; refer to it for context) |
| [docs/AWS_ONLY_ARCHITECTURE.md](docs/AWS_ONLY_ARCHITECTURE.md) | AWS-only architecture; DynamoDB as target DB |

## Local development

### 1. Virtualenv and dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux; Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Environment variables

Copy the example env and set required values:

```bash
cp .env.example .env
```

Edit `.env`. **Required** for the app to start:

- `DATABASE_URL` – e.g. `postgresql+psycopg2://user:password@localhost:5432/scholar` (use `postgresql+psycopg2://` when using psycopg2)
- `JWT_SECRET_KEY` – any non-empty string (use a strong secret in production)
- `AWS_S3_BUCKET` – bucket name (can be a placeholder for local dev if you don’t call S3 yet)

Optional: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SES_FROM_EMAIL`, `FRONTEND_ORIGIN`.

### 3. Database

- **With Docker:** start Postgres and the API together:

```bash
docker compose up --build
```

- **Without Docker:** ensure PostgreSQL is running and `DATABASE_URL` in `.env` is correct. Create tables (or use Alembic):

```bash
# Optional: generate and run migrations
alembic revision -m "init" --autogenerate
alembic upgrade head
```

- **Create root user** (to log in to the dashboard as admin):

```bash
.venv/bin/python3 scripts/seed_root_user.py
```

Then log in at http://localhost:8000/login with **Email:** `root@localhost`, **Password:** `root123`.

### 4. Run the API

**With Docker:** the API runs in the container (see above).

**Without Docker:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open the frontend and docs

- **Frontend (landing page):** http://localhost:8000/ – Scholarvalley–style homepage (header, hero, services, about, contact).
- **API docs (Swagger):** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **Health:** http://localhost:8000/health  

Use the “Authorize” button in Swagger to set a Bearer token after logging in.

## Configuration reference

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL URL; use `postgresql+psycopg2://...` with psycopg2 |
| `JWT_SECRET_KEY` | Secret for signing JWTs (required) |
| `JWT_ALGORITHM` | Default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime |
| `AWS_REGION` | e.g. `us-east-1` |
| `AWS_S3_BUCKET` | S3 bucket name (required) |
| `STRIPE_SECRET_KEY` | Stripe API key (optional) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (optional) |
| `SES_FROM_EMAIL` | Verified SES sender (optional) |
| `FRONTEND_ORIGIN` | Allowed CORS origin (optional; defaults to `*`) |

On AWS, use **Secrets Manager** or **SSM Parameter Store** and inject these into the ECS task definition (see [AWS architecture](docs/AWS_ARCHITECTURE.md)).

## Deploying to AWS (everything tied to AWS)

The whole stack runs on AWS:

- **Compute:** ECS Fargate (FastAPI in Docker)
- **Database:** Amazon RDS PostgreSQL (or Aurora)
- **Storage:** S3 (documents, presigned uploads)
- **Email:** Amazon SES
- **Secrets:** AWS Secrets Manager or SSM
- **CI/CD:** GitHub Actions → ECR; Terraform for infra

**You deploy from your machine** (with your AWS credentials); nothing can connect to your AWS account from this repo. Steps:

1. **Provision infrastructure** with Terraform (cost-conscious defaults: see **infra/COST.md**):
   ```bash
   cd infra
   terraform init
   export TF_VAR_db_password="your_secure_password"
   terraform apply
   ```
   See **[infra/README.md](infra/README.md)** for details and required variables.

2. **Build and push** the app image to ECR (see `infra/README.md`), then set **DATABASE_URL** and **JWT_SECRET_KEY** in the ECS task (e.g. from Secrets Manager).

3. **Architecture and IAM:** See **[docs/AWS_ARCHITECTURE.md](docs/AWS_ARCHITECTURE.md)** for the full mapping of components to AWS services and how to wire secrets and permissions.

4. **CI/CD:** Use **`.github/workflows/deploy-aws.yml`** to build the image and push to ECR on push to `main`. Add `AWS_ROLE_ARN` (or AWS keys) in GitHub repo secrets.

## Frontend

The app serves a static frontend at **/** that matches the look and feel of the classic Scholarvalley site (2017-style): navy header with gold accents, hero section, services grid, about, and contact. Assets are in `static/` (HTML, CSS, JS) and are mounted at `/static/`.

## API overview

| Area | Prefix | Description |
|------|--------|-------------|
| Health | `GET /health` | Liveness check |
| Auth | `/api/auth` | Register, login (JWT), current user |
| Uploads | `/api/uploads` | S3 presigned initiate/complete |
| Payments | `/api/payments` | Stripe checkout session, webhook |
| Tasks | `/api/tasks` | CRUD, list, update status |
| Messages | `/api/messages` | Send, list, mark read |
| Dashboard | `/api/dashboard` | Summary (manager/root) |
| Eligibility | `/api/eligibility` | Rule-based eligibility check |
| ML | `/api/ml` | Consent, recommendation stub |

## Troubleshooting

- **`ValidationError: jwt_secret_key / aws_s3_bucket … Field required`**  
  Set `JWT_SECRET_KEY` and `AWS_S3_BUCKET` in `.env` (see step 2 above).

- **`InvalidRequestError: Attribute name 'metadata' is reserved`**  
  The `AuditLog` model uses `extra_data` instead of `metadata` (reserved by SQLAlchemy). Ensure you’re on the latest code.

- **`http://localhost:8000/docs` not loading (e.g. -102)**  
  Start the server first (`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` or `docker compose up`). Then open http://localhost:8000/docs or http://127.0.0.1:8000/docs.

- **Database connection errors**  
  Use `postgresql+psycopg2://...` in `DATABASE_URL` when using the psycopg2 driver. Ensure PostgreSQL is running and the database exists.

## Changes completed (summary)

- **Phase 0–2:** Project skeleton, Dockerfile, docker-compose, config (Pydantic Settings with `extra="ignore"`), User model, JWT auth, register/login, RBAC.
- **Phase 1:** All SQLModel models (User, Applicant, DocumentBundle, Document, Task, Message, Payment, AuditLog, MLTrainingConsent, EligibilityResult); Alembic env and script location.
- **Phase 2–3:** Auth and S3 presigned uploads; upload endpoints use DB session for audit logging.
- **Phase 4–5:** Stripe checkout + webhook; SES email helper; audit logging on payment events.
- **Phase 6:** Tasks and messages APIs; dashboard summary (accepted clients, pending tasks, revenue).
- **Phase 7:** Eligibility checker endpoint and EligibilityResult storage.
- **Phase 8:** ML consent and ML recommendation stub.
- **Phase 9:** AuditLog model (`extra_data` field), `log_event` helper, CORS from `FRONTEND_ORIGIN`.
- **Fixes:** AuditLog `metadata` → `extra_data` (SQLAlchemy reserved name); uploads inject DB session for `log_event`; eligibility uses `model_dump()`; dashboard revenue query uses `select_from(Payment)`; email validation via Pydantic validators (no `email-validator` dependency); README and troubleshooting updated.
