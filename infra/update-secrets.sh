#!/bin/bash
# Update Secrets Manager with DATABASE_URL and JWT_SECRET_KEY
# Usage: ./update-secrets.sh [db_password]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Get Terraform outputs
SECRET_NAME=$(terraform output -raw secrets_manager_secret_name 2>/dev/null || echo "")
RDS_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "")
RDS_DB_NAME=$(terraform output -raw rds_database_name 2>/dev/null || echo "scholarvalley")
DB_USERNAME="scholarvalley"

if [ -z "$SECRET_NAME" ]; then
    echo "❌ Error: Could not get secret name from Terraform outputs"
    echo "   Make sure Terraform has been applied: terraform apply"
    exit 1
fi

if [ -z "$RDS_ENDPOINT" ]; then
    echo "⚠️  Warning: RDS endpoint not found. Using existing DATABASE_URL from secret or skipping."
    USE_EXISTING_DB_URL=true
else
    USE_EXISTING_DB_URL=false
fi

# Get database password
if [ -n "$1" ]; then
    DB_PASSWORD="$1"
elif [ -n "$TF_VAR_db_password" ]; then
    DB_PASSWORD="$TF_VAR_db_password"
else
    echo "🔐 Enter database password:"
    read -s DB_PASSWORD
fi

# Generate JWT secret if not provided
if [ -z "$JWT_SECRET" ]; then
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
    else
        echo "⚠️  openssl not found. Generating random string..."
        JWT_SECRET=$(head -c 32 /dev/urandom | base64 | tr -d '\n' | head -c 64)
    fi
fi

# Build DATABASE_URL
if [ "$USE_EXISTING_DB_URL" = "false" ]; then
    DATABASE_URL="postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME}"
else
    # Try to get existing DATABASE_URL from secret
    EXISTING_SECRET=$(aws secretsmanager get-secret-value --secret-id "$SECRET_NAME" --query SecretString --output text 2>/dev/null || echo "{}")
    EXISTING_DB_URL=$(echo "$EXISTING_SECRET" | grep -o '"DATABASE_URL":"[^"]*' | cut -d'"' -f4 || echo "")
    if [ -n "$EXISTING_DB_URL" ]; then
        DATABASE_URL="$EXISTING_DB_URL"
        echo "✅ Using existing DATABASE_URL from secret"
    else
        echo "❌ Error: Could not determine DATABASE_URL"
        exit 1
    fi
fi

# Create/update secret
SECRET_JSON=$(cat <<EOF
{
  "DATABASE_URL": "${DATABASE_URL}",
  "JWT_SECRET_KEY": "${JWT_SECRET}"
}
EOF
)

echo "📝 Updating secret: $SECRET_NAME"
aws secretsmanager put-secret-value \
    --secret-id "$SECRET_NAME" \
    --secret-string "$SECRET_JSON" \
    > /dev/null 2>&1 || \
aws secretsmanager create-secret \
    --name "$SECRET_NAME" \
    --description "Scholarvalley application secrets" \
    --secret-string "$SECRET_JSON" \
    > /dev/null

echo "✅ Secret updated successfully!"
echo ""
echo "Next: Force ECS service to redeploy with new secrets:"
echo "  aws ecs update-service --cluster $(terraform output -raw cluster_name) --service $(terraform output -raw service_name) --force-new-deployment"
