# Troubleshooting Guide – Scholarvalley Operating System

Use this guide when something fails. **Environment: macOS (MacBook), Terminal/zsh.** For full context see `docs/CODEBASE_CONTEXT.md`.

---

## 1. Docker

### "Cannot connect to the Docker daemon" / "Is the docker daemon running?"

- **Cause:** Docker Desktop is not running.
- **Fix:** Open **Docker Desktop** from Applications; wait until the menu bar icon shows "Docker Desktop is running". Then run `docker ps` to confirm.

### "permission denied" connecting to Docker socket

- **Cause:** Docker Desktop not running, or your user cannot access the socket.
- **Fix:** Start Docker Desktop. On Mac, Docker Desktop manages the socket; no need to add your user to a `docker` group.

### `docker compose up` fails with "no space left" or build errors

- **Cause:** Disk full or Docker cache/image issues.
- **Fix:** Prune: `docker system prune -a` (removes unused images/containers). Free disk space. Ensure Docker Desktop has enough disk in Settings → Resources.

---

## 2. Database (PostgreSQL)

### "Database connection failed" / "could not connect to server"

- **Local (docker-compose):** Ensure the `db` container is running: `docker compose ps`. Start stack: `docker compose up -d`.
- **DATABASE_URL:** Must be correct. For local Compose: `postgresql+psycopg2://scholarvalley:scholarvalley@db:5432/scholarvalley` (host `db` = service name). For local host: `localhost` instead of `db`.
- **AWS (RDS):** Check Terraform output `rds_endpoint`; security group allows ECS → RDS on 5432; Secrets Manager secret has correct `DATABASE_URL`.

### "Database authentication failed" / "password authentication failed"

- **Cause:** Wrong user/password in `DATABASE_URL` or in Secrets Manager (on AWS).
- **Fix:** Align `.env` (local) or Secrets Manager (AWS) with actual DB credentials. For RDS, use the password you set in `TF_VAR_db_password` and `infra/update-secrets.sh`.

### "relation does not exist" / "no such table"

- **Cause:** Migrations not applied.
- **Fix (local):** `docker compose exec api alembic upgrade head`.  
- **Fix (AWS):** Run migrations against RDS (e.g. one-off task or `docker run` with `DATABASE_URL` and `alembic upgrade head`).

---

## 3. Application startup

### "ValidationError" / "JWT_SECRET_KEY" or "AWS_S3_BUCKET" missing

- **Cause:** Required env vars not set (see `app/core/config.py`).
- **Fix:** Copy `.env.example` to `.env` and set at least `DATABASE_URL`, `JWT_SECRET_KEY`, `AWS_S3_BUCKET`. For local dev, `AWS_S3_BUCKET` can be a placeholder if you don’t call S3.

### "extra_forbidden" when loading settings

- **Cause:** Old env vars (e.g. `ALEMBIC_DB_URL`, `APP_SECRET`) and Pydantic not ignoring extras.  
- **Fix:** Current `config.py` uses `extra="ignore"`. Ensure you’re on the latest code; remove or rename any env var that shouldn’t be in Settings if you have a custom list.

### App runs but 500 on first request

- **Cause:** DB connection or migration issue.
- **Fix:** Check logs; run migrations; verify `DATABASE_URL` and that DB is reachable.

---

## 4. Frontend / API responses

### "Unexpected token 'I', \"Internal S\"... is not valid JSON"

- **Cause:** Server returned non-JSON (e.g. HTML error page or "Internal Server Error" string); frontend called `response.json()`.
- **Fix:** Backend: global exception handler in `app/main.py` returns JSON. Frontend: use `parseJson(r)` (read `response.text()`, then parse). Ensure you’re on versions that include this fix.

### CORS errors in browser

- **Cause:** Frontend origin not allowed.
- **Fix:** Set `FRONTEND_ORIGIN` in env to the frontend URL (e.g. `http://localhost:3000`). If unset, the app may allow `*`; check `app/main.py` CORS config.

---

## 5. AWS deployment

### `aws configure` – no prompts / "credentials not configured"

- **Cause:** AWS CLI not installed or not in PATH.
- **Fix (macOS):** `brew install awscli`, then `aws configure` (Access Key, Secret Key, region).

### Terraform "Error acquiring the state lock" / "state locked"

- **Cause:** Another process holds the lock or a previous run crashed.
- **Fix:** If no other process is running: `terraform force-unlock <LOCK_ID>` (use the ID from the error). Use with care.

### Terraform "db_password" required / variable not set

- **Cause:** RDS is created (`create_rds = true`) and `db_password` is not set.
- **Fix:** `export TF_VAR_db_password="your_secure_password"` or `terraform apply -var="db_password=..."`.

### ECS task keeps stopping / failing health checks

- **Cause:** App crash, wrong env/secrets, or health check path wrong.
- **Fix:** Check ECS task logs in CloudWatch (`/ecs/<cluster-name>`). Verify `/health` returns 200. Ensure Secrets Manager secret has correct `DATABASE_URL` and `JWT_SECRET_KEY`; task execution role can read the secret. Force new deployment after fixing: `aws ecs update-service --cluster <name> --service <name> --force-new-deployment`.

### "Cannot pull image" / ECR login expired

- **Cause:** ECR login token expired (12h).
- **Fix:** Re-run: `aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com`, then push again.

### Terraform: "The state file has no outputs defined or all are empty"

- **Cause:** No successful `terraform apply` has been run yet, or state was left without outputs (e.g. failed apply, or running a script that calls `terraform output` before apply).
- **Fix:** Run a full apply, then refresh so outputs are in state:
  ```bash
  cd infra
  export TF_VAR_db_password="your_secure_password"
  terraform apply -auto-approve
  terraform refresh
  ```
  Then re-run `./deploy.sh` or `./update-secrets.sh`. The deploy script now runs `terraform refresh` after apply and checks for outputs before continuing.

### Terraform: "You are not authorized" (e.g. ec2:DescribeVpcs)

- **Cause:** The IAM user used by `aws configure` lacks permissions. Terraform needs EC2 (VPC, subnets), ECR, S3, RDS, ECS, ELB, IAM, Secrets Manager, CloudWatch Logs, etc.
- **Fix:** An account admin must add permissions. Two options:
  - **Custom policy (recommended):** In **IAM → Users → [your user] → Add permissions → Create inline policy → JSON**, paste the contents of **`infra/iam-policy-terraform-deploy.json`** from this repo. Name it e.g. **ScholarvalleyTerraformDeploy**. Save and run `./deploy.sh` again.
  - **Dev only:** Attach the managed policy **AdministratorAccess** to your user.
  The deploy script checks for `ec2:DescribeVpcs` before running Terraform and will print these instructions if permissions are missing.

---

## 6. Git

### "origin does not appear to be a git repository"

- **Cause:** No remote named `origin`.
- **Fix:** Create a repo on GitHub (e.g. under username **scholarvalley**), then add remote and push. Canonical URL: `https://github.com/scholarvalley/Scholarvalley_Operating_System.git`
  ```bash
  git remote add origin https://github.com/scholarvalley/Scholarvalley_Operating_System.git
  git push -u origin main
  ```
  SSH: `git remote add origin git@github.com:scholarvalley/Scholarvalley_Operating_System.git`

---

## 7. macOS-specific

### "command not found: brew"

- **Cause:** Homebrew not installed.
- **Fix:** Install: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`, then add to PATH as instructed.

### "pip install brew" fails / FileNotFoundError: requirements.txt

- **Cause:** You tried to install **Homebrew** via pip. Homebrew is not a Python package; the PyPI package "brew" is unrelated.
- **Fix:** Install Homebrew with the script above. Do not use `pip install brew` for the macOS package manager.

### `./deploy.sh` – "nothing happens"

- **Cause:** Script may be waiting for **silent** password input (`read -s`).
- **Fix:** When you see "Enter a secure password...", type the password (no characters will show), then press Enter. Or run with debug: `bash -x deploy.sh` to see where it stops.

---

## Getting more help

- **Logs (local):** `docker compose logs -f api`  
- **Logs (AWS):** CloudWatch Logs for `/ecs/<cluster-name>`  
- **Context:** `docs/CODEBASE_CONTEXT.md`  
- **Changelog:** `docs/CHANGELOG.md`  
- **Prompt log (for AI):** `docs/PROMPT_LOG.md`
