# Scholarvalley Operating System – Codebase Context

This file provides a single reference for the **entire codebase context**. Use it to understand structure, conventions, and where things live. **Target: AWS-only architecture** (see `AWS_ONLY_ARCHITECTURE.md`); current implementation uses PostgreSQL (RDS) with a path to DynamoDB.

---

## Project overview

- **Name:** Scholarvalley Operating System (backend + static frontend).
- **Purpose:** Backend API for Scholarvalley (applicants, documents, auth, payments, tasks, messages, eligibility, ML consent). Serves static frontend and runs on AWS (ECS Fargate, RDS, S3, etc.).
- **Platform:** macOS (MacBook); all commands and paths assume Terminal/zsh, Homebrew, Docker Desktop for Mac.
- **Architecture direction:** Use **only AWS services**; database target is **DynamoDB** (or AWS-managed DB). See `docs/AWS_ONLY_ARCHITECTURE.md`.

---

## Tech stack (current)

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Web framework | FastAPI |
| ORM / DB layer | SQLModel (SQLAlchemy), PostgreSQL (psycopg2) |
| Migrations | Alembic |
| Auth | JWT (python-jose), passlib/bcrypt, RBAC (client / manager / root) |
| Storage | Amazon S3 (presigned URLs via boto3) |
| Email | Amazon SES (boto3) |
| Payments | Stripe (checkout + webhook) |
| Config | pydantic-settings, `.env` |
| Container | Docker; ECS Fargate on AWS |

---

## Repository layout

```
Scholarvalley_Operating_System/
├── app/
│   ├── main.py              # FastAPI app, CORS, global exception handler, static mount, routes
│   ├── core/
│   │   ├── config.py        # Settings (DATABASE_URL, JWT_*, AWS_*, Stripe, SES)
│   │   └── security.py      # JWT create/verify, password hash/verify
│   ├── db/
│   │   └── session.py       # SQLModel/SQLAlchemy session, get_session
│   ├── deps.py              # get_current_user, role checks
│   ├── api/
│   │   ├── auth.py          # POST /register, /login
│   │   ├── applicants.py   # CRUD applicants, list (filter by role)
│   │   ├── documents.py    # Document bundles initiate/complete (S3)
│   │   ├── uploads.py      # Presigned upload initiate/complete, audit
│   │   ├── payments.py     # Stripe checkout session, webhook
│   │   ├── tasks.py        # Tasks CRUD, status
│   │   ├── messages.py     # Messages CRUD, read
│   │   ├── dashboard.py    # Summary (revenue, counts)
│   │   ├── eligibility.py  # Eligibility check
│   │   └── ml.py           # ML consent, recommendation stub
│   ├── models/              # SQLModel models (User, Applicant, Document, Task, Message, Payment, AuditLog, etc.)
│   ├── schemas/             # Pydantic request/response schemas
│   └── services/
│       ├── audit.py         # log_event (audit log)
│       └── email.py         # SES send (stub/optional)
├── static/                  # Static frontend (HTML, JS, CSS, assets)
├── alembic/                  # Migrations
├── scripts/
│   ├── seed_root_user.py    # Creates root@localhost / root123
│   └── validate_archive_pages.py
├── infra/                   # Terraform: S3, ECR, RDS, ECS, ALB, Secrets Manager
├── docs/                    # Architecture, guides, context, changelog, prompt log
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml       # Local: api + postgres:15
└── README.md
```

---

## API routes (prefixes)

| Prefix | Module | Main endpoints |
|--------|--------|-----------------|
| `/api/auth` | auth | POST register, login |
| `/api/applicants` | applicants | POST /, GET /, GET /{id}, GET /{id}/bundle |
| `/api` (documents) | documents | POST bundles/{id}/documents/initiate, POST documents/{id}/complete |
| `/api/uploads` | uploads | POST initiate, complete |
| `/api/payments` | payments | POST checkout-session, webhook |
| `/api/tasks` | tasks | POST /, GET /, PATCH /{id}/status |
| `/api/messages` | messages | POST /, GET /, POST /{id}/read |
| `/api/dashboard` | dashboard | GET summary |
| `/api/eligibility` | eligibility | POST check |
| `/api/ml` | ml | POST consent, recommendation |

Root: `/health`, `/`, `/about`, `/services`, `/contact`, `/register`, `/login`, `/dashboard` (static HTML).

---

## Key models (SQLModel / PostgreSQL)

- **User** – email, hashed password, role (client | manager | root).
- **Applicant** – owner_id (User), profile fields.
- **DocumentBundle** / **Document** – S3 keys, status.
- **Task**, **Message** – linked to applicants/users.
- **Payment** – Stripe-related fields.
- **AuditLog** – event type, extra_data (not `metadata`; reserved).
- **MLTrainingConsent**, **EligibilityResult**.

---

## Configuration (env)

- **Required:** `DATABASE_URL`, `JWT_SECRET_KEY`, `AWS_S3_BUCKET`.
- **Optional:** `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `STRIPE_*`, `SES_FROM_EMAIL`, `FRONTEND_ORIGIN`.
- `config.py` normalizes `DATABASE_URL` to `postgresql+psycopg2://`; `extra="ignore"` for unknown vars.

---

## Infra (Terraform)

- **Resources:** S3, ECR, RDS (optional), ECS Fargate, ALB, Secrets Manager secret, IAM (execution + task), security groups.
- **Secrets:** ECS task pulls `DATABASE_URL` and `JWT_SECRET_KEY` from Secrets Manager.
- **Scripts:** `infra/deploy.sh`, `infra/update-secrets.sh`, `infra/setup-prerequisites.sh`.
- **Docs:** `infra/README.md`, `infra/DEPLOYMENT_GUIDE.md`, `infra/COST.md`.

---

## Conventions

- **macOS:** All commands and paths for MacBook (Terminal, zsh, Homebrew, Docker Desktop).
- **Errors:** Global exception handler returns JSON `{ "detail", "error" }`; DB errors sanitized for clients.
- **Frontend:** Uses `parseJson(response)` (response.text then JSON.parse) to avoid "Unexpected token" on non-JSON (e.g. 500).
- **Auth:** JWT in Authorization header; roles enforced in `deps.py` and per-route.

---

## Logs and prompts

- **All logs are updated with new prompts.** On every new user prompt, update: (1) `docs/PROMPT_LOG.md` (add the prompt), (2) `docs/CHANGELOG.md` (if there are changes or doc updates), (3) any other log files. See `docs/PROMPT_LOG.md` for the full rule.

## Related docs

- **Changes over time:** `docs/CHANGELOG.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Developer setup:** `docs/DEVELOPER_SETUP.md`
- **Onboarding:** `docs/ONBOARDING.md`
- **Prompt log (AI context):** `docs/PROMPT_LOG.md`
- **AWS-only / DynamoDB direction:** `docs/AWS_ONLY_ARCHITECTURE.md`
