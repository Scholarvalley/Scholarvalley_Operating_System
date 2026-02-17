# Scholarvalley – AWS infrastructure (Terraform)

This folder provisions AWS resources so the whole app runs on AWS: **RDS PostgreSQL**, **S3**, **ECR**, **ECS Fargate**, and an **ALB**. Defaults are set to **keep cost low** (~\$40–50/month in dev; see [COST.md](COST.md)).

**Who runs the deploy:** You run Terraform and the Docker push from your own machine (or CI) with **your** AWS credentials. Nothing in this repo can connect to your AWS account automatically.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- AWS CLI configured (e.g. `aws configure`) with permissions to create the resources below
- For RDS: set a secure `db_password` (see below)

**Install on macOS:** Run `./setup-prerequisites.sh` (uses Homebrew). If Homebrew is not installed, install it first, then run the script. Alternatively:
- **AWS CLI:** [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) or `brew install awscli`
- **Terraform:** [Download](https://www.terraform.io/downloads) or `brew install terraform`

## Deploy from your machine (you need AWS access)

All steps use **your** AWS account. Configure the AWS CLI with credentials that can create the resources (VPC/EC2, RDS, ECS, S3, ECR, IAM, etc.):

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and region (e.g. us-east-1)
```

Then run the steps below. No automated tool can “connect” to your account from here; you run these commands locally.

## Quick start

1. **Initialize Terraform**
   ```bash
   cd infra
   terraform init
   ```

2. **Plan and apply** (set a strong `db_password`; required when `create_rds = true`)
   ```bash
   export TF_VAR_db_password="your_secure_rds_password_here"
   terraform plan
   terraform apply
   ```
   To **skip RDS** and use an existing database, add `-var="create_rds=false"` (you must set `DATABASE_URL` in the task manually).

3. **Build and push the Docker image** so ECS can run it
   ```bash
   aws ecr get-login-password --region $(terraform output -raw aws_region) | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_uri | cut -d/ -f1)
   docker build -t scholarvalley ../
   docker tag scholarvalley:latest $(terraform output -raw ecr_repository_uri):latest
   docker push $(terraform output -raw ecr_repository_uri):latest
   ```

4. **Set app secrets**  
   The ECS task needs `DATABASE_URL` and `JWT_SECRET_KEY`. Options:
   - **Secrets Manager**: create a secret with key-value pairs and reference it in the task definition (add `secrets` in `container_definitions`).
   - **Manual update**: edit the task definition in the AWS console and add environment variables or secrets, then update the ECS service to use the new revision.

   Use the RDS endpoint from `terraform output rds_endpoint` to build `DATABASE_URL`:
   ```text
   postgresql+psycopg2://USER:PASSWORD@RDS_ENDPOINT:5432/DB_NAME
   ```

5. **Open the API**  
   After the service is healthy:
   ```text
   http://$(terraform output -raw alb_dns_name)
   ```

## What gets created

| Resource | Purpose |
|----------|--------|
| **S3 bucket** | App uploads (documents); optional static assets. Encrypted, no public access. |
| **ECR repository** | Holds the Scholarvalley Docker image. |
| **RDS PostgreSQL** | Database (if `create_rds = true`). Single instance, encrypted. |
| **ECS cluster + Fargate service** | Runs the FastAPI container. |
| **ALB** | Load balancer; forwards HTTP to ECS; `/health` for health checks. |
| **IAM roles** | ECS task can pull images, write logs, access S3 and SES. |
| **Security groups** | ALB (80/443); ECS (8000 from ALB); RDS (5432 from ECS). |

## Variables

See `variables.tf`. Important ones:

- **`db_password`** (required when `create_rds = true`) – RDS master password. Use `TF_VAR_db_password` or `-var "db_password=..."`.
- **`create_rds`** – Set to `false` to skip RDS (e.g. use an existing DB).
- **`environment`** – `dev`, `staging`, or `prod` (affects names and e.g. final snapshot for RDS).
- **`vpc_id`** / **`private_subnet_ids`** – Leave empty to use the default VPC and subnets.

## Tying config to AWS

- **DATABASE_URL**: From RDS output; store in Secrets Manager and inject into the ECS task.
- **JWT_SECRET_KEY**: Generate a long random string; store in Secrets Manager; inject into the task.
- **AWS_S3_BUCKET**: Set in the task definition from Terraform output `s3_bucket_name` (already in `main.tf` env).
- **SES**: Verify your sender in SES; set `SES_FROM_EMAIL` in the task.
- **Stripe**: Put Stripe keys in Secrets Manager and map into the task as env or secrets.

After changing the task definition (e.g. adding secrets), run:
```bash
aws ecs update-service --cluster scholarvalley-dev --service scholarvalley-dev --force-new-deployment
```

## Cost

Defaults are chosen to **minimize cost** (smallest Fargate task, single-AZ RDS, default VPC). See **[COST.md](COST.md)** for rough monthly estimates and ways to reduce spend further.

## Cleanup

```bash
terraform destroy
```
Use `-var "db_password=..."` again if you had set it for RDS.
