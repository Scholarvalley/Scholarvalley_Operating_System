#!/bin/bash
# Scholarvalley – Install AWS deployment prerequisites (macOS)
# Run: ./setup-prerequisites.sh

set -e

echo "Scholarvalley – Prerequisites Setup"
echo "===================================="
echo ""

# 1. Homebrew (recommended for macOS)
if ! command -v brew &>/dev/null; then
    echo "Homebrew is not installed."
    echo ""
    echo "Install Homebrew first (paste in Terminal):"
    echo ""
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "Then add Homebrew to your PATH (instructions shown after install)."
    echo "After that, run this script again, or run:"
    echo "  brew install awscli terraform"
    echo ""
    exit 1
fi

echo "✅ Homebrew found"
echo ""

# 2. AWS CLI
if ! command -v aws &>/dev/null; then
    echo "Installing AWS CLI..."
    brew install awscli
else
    echo "✅ AWS CLI already installed: $(aws --version)"
fi
echo ""

# 3. Terraform
if ! command -v terraform &>/dev/null; then
    echo "Installing Terraform..."
    brew install terraform
else
    echo "✅ Terraform already installed: $(terraform --version | head -n1)"
fi
echo ""

# 4. AWS credentials
if ! aws sts get-caller-identity &>/dev/null 2>&1; then
    echo "⚠️  AWS credentials not configured."
    echo "   Run: aws configure"
    echo "   Enter your Access Key ID, Secret Access Key, and region (e.g. us-east-1)."
    echo ""
else
    echo "✅ AWS credentials configured"
    aws sts get-caller-identity --query 'Account' --output text | xargs -I {} echo "   Account: {}"
fi
echo ""

echo "Setup complete. To deploy:"
echo "  cd infra"
echo "  ./deploy.sh"
echo ""
