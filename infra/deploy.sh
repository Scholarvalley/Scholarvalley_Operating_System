#!/bin/bash
# Scholarvalley AWS Deployment Script
# This script helps deploy the application to AWS using Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Scholarvalley AWS Deployment"
echo "================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it:"
    echo "   macOS: brew install awscli"
    echo "   Or visit: https://aws.amazon.com/cli/"
    exit 1
fi
echo "✅ AWS CLI found: $(aws --version)"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")
echo "✅ AWS credentials configured (Account: $AWS_ACCOUNT, Region: $AWS_REGION)"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it:"
    echo "   macOS: brew install terraform"
    echo "   Or visit: https://www.terraform.io/downloads"
    exit 1
fi
echo "✅ Terraform found: $(terraform --version | head -n1)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"
echo ""

# Check AWS permissions (Terraform needs at least EC2 DescribeVpcs)
echo "🔑 Checking AWS permissions (required for Terraform)..."
if ! aws ec2 describe-vpcs --max-items 1 &>/dev/null; then
    echo ""
    echo "❌ Your IAM user does not have permission to run Terraform (e.g. ec2:DescribeVpcs)."
    echo "   An AWS account admin must attach the required policy to your user."
    echo ""
    echo "   Option 1 – Use the policy in this repo:"
    echo "     1. Open IAM → Users → [your user] → Add permissions → Create inline policy."
    echo "     2. Choose JSON and paste the contents of:"
    echo "        $SCRIPT_DIR/iam-policy-terraform-deploy.json"
    echo "     3. Name the policy e.g. ScholarvalleyTerraformDeploy and save."
    echo ""
    echo "   Option 2 – For dev only: attach AWS managed policy AdministratorAccess to your user."
    echo ""
    echo "   Then run this script again."
    exit 1
fi
echo "✅ AWS permissions OK"
echo ""

# Prompt for database password
if [ -z "$TF_VAR_db_password" ]; then
    echo "🔐 Database Password"
    echo "Enter a secure password for the RDS PostgreSQL database (you won't see it as you type):"
    read -s DB_PASSWORD
    export TF_VAR_db_password="$DB_PASSWORD"
    echo ""
    echo "Password set. Continuing..."
fi

# Change to infra directory
cd "$SCRIPT_DIR"

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan
echo ""
echo "📝 Planning Terraform deployment..."
terraform plan -out=tfplan

# Confirm before applying
echo ""
echo "⚠️  This will create AWS resources (RDS, ECS, S3, ECR, ALB, etc.)"
echo "   Estimated monthly cost: ~\$40-50 (see infra/COST.md)"
read -p "Continue with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Apply
echo ""
echo "🚀 Applying Terraform configuration..."
terraform apply tfplan

# Ensure outputs are in state (fixes "state has no outputs" when state was stale)
echo "Refreshing state for outputs..."
terraform refresh -input=false 2>/dev/null || true

# Get outputs (required)
if ! ECR_REPO=$(terraform output -raw ecr_repository_uri 2>/dev/null) || [ -z "$ECR_REPO" ]; then
    echo "❌ Could not read Terraform outputs. State may have no outputs."
    echo "   Run: cd $SCRIPT_DIR && terraform apply -auto-approve && terraform refresh"
    echo "   Then re-run this script."
    exit 1
fi
AWS_REGION_OUT=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
RDS_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "")
RDS_DB_NAME=$(terraform output -raw rds_database_name 2>/dev/null || echo "scholarvalley")
DB_USERNAME="scholarvalley"

echo ""
echo "✅ Infrastructure deployed!"
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
cd "$PROJECT_ROOT"
docker build -t scholarvalley:latest .

echo ""
echo "📤 Pushing Docker image to ECR..."
aws ecr get-login-password --region "$AWS_REGION_OUT" | \
    docker login --username AWS --password-stdin "$(echo $ECR_REPO | cut -d/ -f1)"

docker tag scholarvalley:latest "${ECR_REPO}:latest"
docker push "${ECR_REPO}:latest"

echo ""
echo "✅ Docker image pushed!"
echo ""

# Update secrets in Secrets Manager
echo "🔐 Setting up secrets in Secrets Manager..."
if [ -f "$SCRIPT_DIR/update-secrets.sh" ]; then
    "$SCRIPT_DIR/update-secrets.sh" "$TF_VAR_db_password"
else
    echo "⚠️  update-secrets.sh not found. Please run it manually:"
    echo "   cd infra && ./update-secrets.sh"
fi
echo ""

# Get cluster and service names
CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "scholarvalley-dev")
SERVICE_NAME=$(terraform output -raw service_name 2>/dev/null || echo "scholarvalley-dev")

# Get ALB URL
ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
API_URL=$(terraform output -raw api_url 2>/dev/null || echo "")

echo "🎉 Deployment Summary"
echo "===================="
echo "ECR Repository: $ECR_REPO"
echo "RDS Endpoint: $RDS_ENDPOINT"
echo "Secrets Manager: $(terraform output -raw secrets_manager_secret_name 2>/dev/null || echo 'N/A')"
if [ -n "$API_URL" ]; then
    echo "API URL: $API_URL"
else
    echo "ALB DNS: $ALB_DNS"
    echo "API URL: http://$ALB_DNS"
fi
echo ""
echo "📋 Next Steps:"
echo "1. Force new ECS deployment to pick up secrets:"
echo "   aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment"
echo ""
echo "2. Wait for service to become healthy (check AWS Console or):"
echo "   aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --query 'services[0].deployments[0].status'"
echo ""
echo "3. Run database migrations (using a temporary task or EC2 instance):"
RDS_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "")
if [ -n "$RDS_ENDPOINT" ]; then
    DB_URL="postgresql+psycopg2://scholarvalley:${TF_VAR_db_password}@${RDS_ENDPOINT}:5432/scholarvalley"
    echo "   docker run --rm -e DATABASE_URL=\"$DB_URL\" ${ECR_REPO}:latest alembic upgrade head"
    echo "   docker run --rm -e DATABASE_URL=\"$DB_URL\" ${ECR_REPO}:latest python scripts/seed_root_user.py"
else
    echo "   (RDS endpoint not available - check Terraform outputs)"
fi
echo ""
echo "4. Test the API:"
if [ -n "$API_URL" ]; then
    echo "   curl $API_URL/health"
else
    echo "   curl http://$ALB_DNS/health"
fi
echo ""
