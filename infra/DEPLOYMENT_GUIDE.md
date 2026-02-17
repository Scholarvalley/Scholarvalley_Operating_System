# AWS Deployment Guide

This guide walks you through deploying Scholarvalley to AWS.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured (`aws configure`)
3. **Terraform** >= 1.0 installed
4. **Docker** installed and running

### Install Prerequisites (macOS)

```bash
# Install AWS CLI
brew install awscli

# Install Terraform
brew install terraform

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, and region (e.g. us-east-1)
```

## Quick Deployment

The easiest way is to use the automated deployment script:

```bash
cd infra
./deploy.sh
```

The script will:
1. Check prerequisites
2. Initialize Terraform
3. Plan and apply infrastructure
4. Build and push Docker image
5. Set up secrets in Secrets Manager
6. Provide next steps

## Manual Deployment Steps

If you prefer to run steps manually:

### 1. Initialize Terraform

```bash
cd infra
terraform init
```

### 2. Set Database Password

```bash
export TF_VAR_db_password="your_secure_password_here"
```

**Important:** Use a strong password. This will be the master password for RDS PostgreSQL.

### 3. Plan and Apply Infrastructure

```bash
terraform plan
terraform apply
```

This creates:
- S3 bucket for uploads
- ECR repository for Docker images
- RDS PostgreSQL database (optional, can skip with `-var="create_rds=false"`)
- ECS cluster and Fargate service
- Application Load Balancer (ALB)
- Security groups and IAM roles
- Secrets Manager secret (empty initially)

**Cost:** ~$40-50/month (see `COST.md`)

### 4. Build and Push Docker Image

```bash
# Get ECR repository URL
ECR_REPO=$(terraform output -raw ecr_repository_uri)
AWS_REGION=$(terraform output -raw aws_region)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $(echo $ECR_REPO | cut -d/ -f1)

# Build and push
cd ..
docker build -t scholarvalley:latest .
docker tag scholarvalley:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest
```

### 5. Set Up Secrets

Update Secrets Manager with `DATABASE_URL` and `JWT_SECRET_KEY`:

```bash
cd infra
./update-secrets.sh
```

Or manually:

```bash
# Get values
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
SECRET_NAME=$(terraform output -raw secrets_manager_secret_name)

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Build DATABASE_URL (replace YOUR_PASSWORD with your actual password)
DATABASE_URL="postgresql+psycopg2://scholarvalley:YOUR_PASSWORD@${RDS_ENDPOINT}:5432/scholarvalley"

# Update secret
aws secretsmanager put-secret-value \
    --secret-id $SECRET_NAME \
    --secret-string "{\"DATABASE_URL\":\"${DATABASE_URL}\",\"JWT_SECRET_KEY\":\"${JWT_SECRET}\"}"
```

### 6. Force ECS Service Redeployment

The task definition already references Secrets Manager, but you need to force a new deployment:

```bash
CLUSTER_NAME=$(terraform output -raw cluster_name)
SERVICE_NAME=$(terraform output -raw service_name)

aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment
```

### 7. Wait for Service to Become Healthy

Check the service status:

```bash
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --query 'services[0].deployments[0].status'
```

Or check in AWS Console: ECS → Clusters → Your cluster → Services → Your service

### 8. Run Database Migrations

Run Alembic migrations to set up the database schema:

```bash
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
ECR_REPO=$(terraform output -raw ecr_repository_uri)
DB_PASSWORD="your_password_here"

docker run --rm \
    -e DATABASE_URL="postgresql+psycopg2://scholarvalley:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/scholarvalley" \
    ${ECR_REPO}:latest \
    alembic upgrade head
```

### 9. Seed Root User (Optional)

Create the initial root user:

```bash
docker run --rm \
    -e DATABASE_URL="postgresql+psycopg2://scholarvalley:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/scholarvalley" \
    ${ECR_REPO}:latest \
    python scripts/seed_root_user.py
```

Default credentials: `root@localhost` / `root123`

### 10. Test the API

Get the ALB URL:

```bash
terraform output api_url
```

Or:

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)
curl http://${ALB_DNS}/health
```

You should see: `{"status":"ok"}`

## Configuration

### Environment Variables

The ECS task definition automatically sets:
- `AWS_REGION` - From Terraform variable
- `AWS_S3_BUCKET` - From Terraform output
- `DATABASE_URL` - From Secrets Manager
- `JWT_SECRET_KEY` - From Secrets Manager

### Additional Secrets

To add more secrets (e.g., Stripe keys):

1. Update the secret in Secrets Manager:
```bash
SECRET_NAME=$(terraform output -raw secrets_manager_secret_name)
aws secretsmanager put-secret-value \
    --secret-id $SECRET_NAME \
    --secret-string file://secrets.json
```

2. Update `infra/main.tf` to add the secret to the task definition:
```hcl
secrets = [
  # ... existing secrets ...
  {
    name      = "STRIPE_SECRET_KEY"
    valueFrom = "${aws_secretsmanager_secret.app.arn}:STRIPE_SECRET_KEY::"
  }
]
```

3. Apply Terraform and redeploy:
```bash
terraform apply
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment
```

## Troubleshooting

### Service Not Starting

1. Check ECS task logs:
```bash
LOG_GROUP=$(terraform output -raw cluster_name | sed 's/$/\/ecs\/&/')
aws logs tail $LOG_GROUP --follow
```

2. Check task status:
```bash
aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN
```

### Database Connection Issues

1. Verify RDS endpoint is correct:
```bash
terraform output rds_endpoint
```

2. Test connection from your machine (if security group allows):
```bash
psql -h $(terraform output -raw rds_endpoint) -U scholarvalley -d scholarvalley
```

3. Check security groups allow ECS → RDS (port 5432)

### ALB Health Check Failing

1. Verify `/health` endpoint works:
```bash
curl http://$(terraform output -raw alb_dns_name)/health
```

2. Check target group health:
```bash
TG_ARN=$(aws elbv2 describe-target-groups --names scholarvalley-dev-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
aws elbv2 describe-target-health --target-group-arn $TG_ARN
```

## Cleanup

To destroy all resources:

```bash
cd infra
terraform destroy
```

**Warning:** This will delete all data, including the RDS database (unless `skip_final_snapshot = false`).

## Cost Optimization

See `COST.md` for cost breakdown and optimization tips.
