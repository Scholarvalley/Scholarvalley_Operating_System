# Developer Setup Guide – Scholarvalley Operating System

This guide gets a **new developer** from zero to running the app locally and deploying to AWS. **Target machine: macOS (MacBook).** All commands assume Terminal (zsh).

---

## 1. Prerequisites

- **macOS** (MacBook).
- **Xcode Command Line Tools** (for git, etc.):  
  `xcode-select --install`  
  if not already installed.
- **Homebrew:**  
  `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`  
  Then follow the instructions to add Homebrew to your PATH.
- **Python 3.11+:**  
  `brew install python@3.11`  
  (or use system Python if 3.11+).
- **Docker Desktop for Mac:**  
  Install from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop). Start Docker Desktop before using `docker` or `docker compose`.
- **Git:**  
  Usually installed with Xcode tools; or `brew install git`.

---

## 2. Configure Git (one-time, on your Mac)

Do this once per machine so your commits have the right name and email.

**Step 1 – Set your name (use your real name or nickname):**
```bash
git config --global user.name "Your Name"
```

**Step 2 – Set your email (use the email tied to your GitHub/GitLab account):**
```bash
git config --global user.email "you@example.com"
```

**Step 3 – Check it:**
```bash
git config --global --list | grep user
```
You should see `user.name` and `user.email`.

**Step 4 – Optional: default branch name**
```bash
git config --global init.defaultBranch main
```

**Step 5 – Optional: credential helper (so you don’t type password every push)**  
For HTTPS, macOS can store credentials in the Keychain:
```bash
git config --global credential.helper osxkeychain
```

---

## 3. Clone and enter project

```bash
# If you have a remote (replace with your repo URL):
git clone https://github.com/YOUR_ORG/Scholarvalley_Operating_System.git
cd Scholarvalley_Operating_System

# Or if you already have the folder:
cd /Users/mac/Desktop/Python/Scholarvalley_Operating_System
```

---

## 4. Python environment (optional for local API dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Environment variables

```bash
cp .env.example .env
```

Edit `.env`. **Minimum to run the app:**

- **DATABASE_URL** – For Docker Compose:  
  `postgresql+psycopg2://scholarvalley:scholarvalley@db:5432/scholarvalley`  
  For local DB on host:  
  `postgresql+psycopg2://scholarvalley:scholarvalley@localhost:5432/scholarvalley`
- **JWT_SECRET_KEY** – Any non-empty string (e.g. `openssl rand -hex 32`).
- **AWS_S3_BUCKET** – Bucket name; can be a placeholder for local dev if you don’t hit S3.

Optional: `STRIPE_*`, `SES_FROM_EMAIL`, `FRONTEND_ORIGIN`.

---

## 6. Run with Docker (recommended)

```bash
docker compose up --build
```

- API: **http://localhost:8000**
- Docs: **http://localhost:8000/docs**
- Health: **http://localhost:8000/health**

Migrations and seed (in another terminal):

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_root_user.py
```

Default root user: `root@localhost` / `root123`.

---

## 7. Run without Docker (API only, DB still in Docker)

Start only Postgres:

```bash
docker compose up -d db
```

Then:

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg2://scholarvalley:scholarvalley@localhost:5432/scholarvalley"
# Ensure .env has JWT_SECRET_KEY and AWS_S3_BUCKET
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 8. AWS (deploy and CLI)

For deployment and AWS CLI/Terraform:

```bash
brew install awscli terraform
aws configure
# Enter Access Key ID, Secret Access Key, region (e.g. us-east-1)
```

Deploy (from project root):

```bash
cd infra
./deploy.sh
```

See `infra/README.md` and `infra/DEPLOYMENT_GUIDE.md` for details.  
**Note:** Project direction is **AWS-only** (including DynamoDB for data). Current Terraform still uses RDS PostgreSQL; see `docs/AWS_ONLY_ARCHITECTURE.md`.

---

## 9. Useful commands

| Task | Command |
|------|---------|
| Run app + DB | `docker compose up --build` |
| Run in background | `docker compose up -d` |
| Migrations | `docker compose exec api alembic upgrade head` |
| Seed root user | `docker compose exec api python scripts/seed_root_user.py` |
| API logs | `docker compose logs -f api` |
| Stop | `docker compose down` |
| Lint/format | Use your preferred tool (e.g. ruff, black) |

---

## 10. Project layout (short)

- **`app/`** – FastAPI app, API routes, models, schemas, services.
- **`static/`** – Static frontend (HTML/JS/CSS).
- **`infra/`** – Terraform (S3, ECR, RDS, ECS, ALB, Secrets Manager).
- **`docs/`** – Architecture, context, changelog, troubleshooting, onboarding, prompt log.
- **`alembic/`** – DB migrations.
- **`scripts/`** – Seed and utility scripts.

Full context: **`docs/CODEBASE_CONTEXT.md`**.  
Troubleshooting: **`docs/TROUBLESHOOTING.md`**.  
Onboarding: **`docs/ONBOARDING.md`**.
