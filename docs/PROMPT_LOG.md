# Prompt Log – Scholarvalley Operating System

**Purpose:** This file is the **single log of user prompts** (and high-level intent) for the project. **Update this file whenever there is a new user prompt.** Any assistant or human should **refer to this file and only make updates that are consistent with both the current prompt and all previous prompts** listed here.

**All logs updated with new prompts:** Whenever there is a **new prompt**, update **all** project logs: (1) **PROMPT_LOG.md** (this file) – add the new prompt; (2) **CHANGELOG.md** – add an entry for any resulting changes or for the prompt-driven doc update; (3) any other log files the project keeps. Keep logs in sync with prompt-driven decisions and changes.

**Format:** Newest prompt at the top. Each entry: date (if known), short prompt summary, and key decisions/constraints that affect the codebase or docs.

---

## How to use this log

- **Before making changes:** Read the latest and relevant past prompts so that updates align with stated goals (e.g. macOS-only, AWS-only, DynamoDB).
- **After a new prompt:** (1) Append a new entry at the top of the "Prompt history" section below; (2) update **all logs** (this file, CHANGELOG.md, and any others) as needed so they reflect the new prompt and any changes made.

---

## Prompt history

### 2025-02 (current session)

- **Prompt:** "on the home page use body3-bg as the first and main background picture..." (home layout and blog setup)
- **Intent:** Refresh home page backgrounds and add a basic blog. Changes: home hero now uses `body3-bg` full-bleed; audience section sits on a solid black background; Document Review signup section uses `body2-bg` as a fixed background so the signup content scrolls over a static image; "Latest from the Blog" section matches the audience background and links to a new `/blog` page; a simple Blog page was added with cards for opportunities and deadlines; navigation on all pages now includes a Blog link; logs (CHANGELOG, PROMPT_LOG) updated.

- **Prompt:** "can you check change logs did we loose anything when restarting the system?"
- **Intent:** Verify nothing was lost after Docker/system restart. Result: Git history intact (commits for black theme, assets/tests/Docker fixes present). CHANGELOG and PROMPT_LOG had not been updated for this session’s work; missing entries were added to CHANGELOG (black theme, home archive layout, assets, pytest, Docker fixes, static cache, frontend tests).

- **Prompt:** "this is the services page please update: https://web.archive.org/web/20171202170317/http://www.scholarvalley.com/services"
- **Intent:** Replace placeholder Services page content with the real content from the 2017 archive (document review pricing, application process, scholarship notification, support email).

- **Prompt:** "this the about page please update: https://web.archive.org/web/20171202165626/http://www.scholarvalley.com/about-us"
- **Intent:** Replace placeholder About page content with the real content from the 2017 archive (Scholarvalley mission, guarantees, headquarters, services, mission statement).

- **Prompt:** "lets test each page based on previous prompt and ensure functionality. keep editing until everything is fixed. ensure all pages are functional"
- **Intent:** Test every frontend page, fix issues, make all pages functional. Changes: About, Services, Contact – real copy and links; register/login/dashboard JS – parseJson handles array detail (FastAPI validation), login redirect from ?next=, dashboard null guards and array/list response handling; register/login form guards; services-list CSS; validate_archive_pages includes register, login, dashboard. All 7 pages pass structure validation.

- **Prompt:** "fix following and redeploy" – Terraform error: state file has no outputs defined or all defined outputs are empty.
- **Intent:** Fix empty Terraform outputs and redeploy. Changes: deploy.sh runs `terraform refresh` after apply and checks for outputs before reading them; update-secrets.sh runs refresh and uses variables for cluster/service in final echo; TROUBLESHOOTING.md updated.

- **Prompt:** "same issue can you continue to attempt deployment until resolved"
- **Intent:** User still has IAM 403 (ec2:DescribeVpcs); wants deployment attempted until it works. Resolution requires an admin to attach the provided IAM policy; added policy JSON and deploy script.

- **Prompt:** User hit Terraform error: Thibaut_A not authorized for ec2:DescribeVpcs (403 UnauthorizedOperation) on data.aws_vpc.default.
- **Intent:** Fix AWS IAM permissions so Terraform can run (EC2 and other services).

- **Prompt:** "next step for deployment"
- **Intent:** User wants the next step(s) to deploy the application (AWS deployment).

- **Prompt:** "this link is correct for git: https://github.com/scholarvalley/Scholarvalley_Operating_System.git update docs and code"
- **Intent:** Use this exact Git URL everywhere in docs and code (lowercase scholarvalley).

- **Prompt:** "what is the next step ?"
- **Intent:** User wants the recommended next action(s) after successful GitHub push.

- **Prompt:** Push was successful; "lets not change anything."
- **Intent:** Push succeeded. User later confirmed the **correct** Git URL is `https://github.com/scholarvalley/Scholarvalley_Operating_System.git` (lowercase); docs and code updated to use this URL everywhere.

- **Prompt:** "lets create a new repo and push git" (after "Repository not found" for scholarvalley/Scholarvalley_Operating_System)
- **Intent:** Create the GitHub repository (it doesn’t exist yet), then push the local project to it.

- **Prompt:** "username is scholarvalley please update for git"
- **Intent:** Use GitHub username **scholarvalley** in Git remote URLs and any docs/examples (replace YOUR_USERNAME with scholarvalley).

- **Prompt:** "now lets commit and push the complete project to git"
- **Intent:** Commit all current changes and push the full project to the remote (GitHub). Ensure nothing is left uncommitted.

- **Prompt:** "give me step by step on how to confi git"
- **Intent:** Step-by-step guide to configure Git (identity, remote, etc.) on macOS.

- **Prompt:** "what is the next step"
- **Intent:** User wants to know the recommended next action(s). See ordered list below (commit docs, deploy AWS, push Git).

- **Prompt:** "all logs should updated with new prompts"
- **Intent:** Whenever there is a new user prompt, **all** logs (PROMPT_LOG, CHANGELOG, and any other log files) must be updated accordingly. No log should be left stale.
- **Decisions:** PROMPT_LOG.md now states this rule at the top and in "How to use this log". CHANGELOG and other logs will be updated on each new prompt when changes occur.

- **Prompt:** Keep a file with context of the entire codebase; keep a log of all changes; write troubleshooting guide; developer setup guide; onboarding guide; write a log file that tracks all previous and future prompts, update it on every new prompt, and refer to it so updates consider current and previous prompts; **everything should be AWS-based; for database use DynamoDB or an AWS service; use only AWS services.**
- **Decisions/constraints:**
  - **AWS-only:** All services should be AWS where possible (compute, storage, DB, secrets, etc.). Database: **DynamoDB** (or another AWS-native DB), not third-party or self-hosted DB.
  - **Documentation:** Created/updated: `CODEBASE_CONTEXT.md`, `CHANGELOG.md`, `TROUBLESHOOTING.md`, `DEVELOPER_SETUP.md`, `ONBOARDING.md`, `PROMPT_LOG.md`, `AWS_ONLY_ARCHITECTURE.md`.
  - **Prompt log:** This file; must be updated on every new prompt; all updates must consider current and previous prompts.

- **Prompt:** "can you check now and see how we are looking"  
- **Intent:** Verify current state (Docker, git, AWS). Result: Docker running (api + db), API 200, AWS configured, git with uncommitted README changes.

- **Prompt:** "i want you to keep in mind that i am running this from a macbook"  
- **Intent:** All instructions and docs should assume macOS (MacBook). Added "On macOS (MacBook)" in main README and infra README.

- **Prompt:** "provide me next step code"  
- **Intent:** Give exact next commands for deployment (cd infra, ./deploy.sh and manual alternative).

- **Prompt:** "AWS has been configured can you double check"  
- **Intent:** Verify AWS CLI/credentials. Checked with `aws sts get-caller-identity` and `aws configure list`.

- **Prompt:** "why i am having this error" (pip install brew / FileNotFoundError: requirements.txt)  
- **Intent:** Clarify that Homebrew is not a Python package; fix confusion between PyPI "brew" and macOS Homebrew.

- **Prompt:** "lets try again to launch it on AWS account"  
- **Intent:** Deploy app to AWS. Added Terraform Secrets Manager, deploy/update-secrets/setup-prerequisites scripts, deployment guide; documented steps for macOS.

- **Prompt:** "update git"  
- **Intent:** Initialize git, add .gitignore, initial commit. Done; later added remote instructions for GitHub.

- **Prompt:** "push to git"  
- **Intent:** Commit and push. Committed infra changes; push failed until user adds `origin` remote.

- **Prompt:** "next step is docker"  
- **Intent:** Docker next steps: docker compose up, migrations, seed, build for ECR.

- **Prompt:** "what is the next step"  
- **Intent:** Ordered next steps: run locally with Docker, then deploy to AWS, then post-deploy steps, then push to GitHub.

- **Prompt:** "is the docker daemon running?"  
- **Intent:** Check Docker. Result: daemon was not running; user instructed to start Docker Desktop.

- **Prompt:** "nothing is happening" (re deploy.sh)  
- **Intent:** Script waiting for silent password input; clarified and improved deploy.sh prompt.

---

## Persistent constraints (from prompts)

- **macOS:** All commands, paths, and tooling assume **MacBook, Terminal, zsh, Homebrew, Docker Desktop**. No Windows or Linux-specific defaults unless explicitly requested.
- **GitHub:** Canonical Git URL: `https://github.com/scholarvalley/Scholarvalley_Operating_System.git`. Username **scholarvalley** for all remote URLs and repo references.
- **AWS-only:** Prefer **only AWS services** (compute, DB, storage, secrets, etc.). **Database:** use **DynamoDB** or another AWS-native data store as the target; current implementation still uses RDS PostgreSQL until migration is done.
- **Documentation:** Maintain CODEBASE_CONTEXT.md, CHANGELOG.md, TROUBLESHOOTING.md, DEVELOPER_SETUP.md, ONBOARDING.md, PROMPT_LOG.md; **update all logs with new prompts** (PROMPT_LOG + CHANGELOG + any other logs); reference prompt log when making changes.
