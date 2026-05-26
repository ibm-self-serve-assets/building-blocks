#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Confluent Cloud Streaming Solution Setup                ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check prerequisites
echo -e "${BLUE}[1/6] Checking Prerequisites...${NC}"
echo ""

MISSING_DEPS=0

if command_exists terraform; then
    TERRAFORM_VERSION=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)
    print_status "Terraform installed (version $TERRAFORM_VERSION)"
else
    print_error "Terraform not found. Please install Terraform >= 1.0"
    print_info "Visit: https://www.terraform.io/downloads"
    MISSING_DEPS=1
fi

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 installed (version $PYTHON_VERSION)"
else
    print_error "Python 3 not found. Please install Python >= 3.8"
    print_info "Visit: https://www.python.org/downloads/"
    MISSING_DEPS=1
fi

if command_exists pip3; then
    print_status "pip3 installed"
else
    print_error "pip3 not found. Please install pip3"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    print_error "Missing required dependencies. Please install them and try again."
    exit 1
fi

echo ""

# Check for Confluent Cloud credentials
echo -e "${BLUE}[2/6] Checking Confluent Cloud Credentials...${NC}"
echo ""

if [ ! -f "$PROJECT_ROOT/terraform/terraform.tfvars" ]; then
    print_warning "terraform.tfvars not found"
    print_info "Creating from example..."
    
    if [ -f "$PROJECT_ROOT/terraform/terraform.tfvars.example" ]; then
        cp "$PROJECT_ROOT/terraform/terraform.tfvars.example" "$PROJECT_ROOT/terraform/terraform.tfvars"
        print_status "Created terraform.tfvars"
        echo ""
        print_warning "Please edit terraform/terraform.tfvars with your Confluent Cloud credentials:"
        print_info "  - api_key: Your Confluent Cloud API key"
        print_info "  - api_secret: Your Confluent Cloud API secret"
        echo ""
        read -p "Press Enter after updating terraform.tfvars..."
    else
        print_error "terraform.tfvars.example not found"
        exit 1
    fi
else
    print_status "terraform.tfvars found"
fi

echo ""

# Initialize and deploy Terraform
echo -e "${BLUE}[3/6] Deploying Infrastructure with Terraform...${NC}"
echo ""

cd "$PROJECT_ROOT/terraform"

print_info "Running terraform init..."
if terraform init; then
    print_status "Terraform initialized"
else
    print_error "Terraform init failed"
    exit 1
fi

echo ""
print_info "Running terraform validate..."
if terraform validate; then
    print_status "Terraform configuration valid"
else
    print_error "Terraform validation failed"
    exit 1
fi

echo ""
print_info "Running terraform plan..."
terraform plan -out=tfplan

echo ""
print_warning "Review the plan above. This will create resources in Confluent Cloud."
read -p "Continue with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_info "Deployment cancelled"
    rm -f tfplan
    exit 0
fi

echo ""
print_info "Running terraform apply..."
if terraform apply tfplan; then
    print_status "Infrastructure deployed successfully"
    rm -f tfplan
else
    print_error "Terraform apply failed"
    rm -f tfplan
    exit 1
fi

echo ""

# Setup Python environment
echo -e "${BLUE}[4/6] Setting up Python Environment...${NC}"
echo ""

cd "$PROJECT_ROOT/python"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Recreate it? (yes/no): " RECREATE
    if [ "$RECREATE" = "yes" ]; then
        rm -rf venv
        print_info "Removed existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    if python3 -m venv venv; then
        print_status "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Installing Python dependencies..."
if pip install -r requirements.txt; then
    print_status "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

echo ""

# Verify .env file
echo -e "${BLUE}[5/6] Verifying Configuration...${NC}"
echo ""

if [ -f ".env" ]; then
    print_status ".env file generated by Terraform"
    
    # Check if .env has required variables
    REQUIRED_VARS=("KAFKA_BOOTSTRAP_SERVERS" "KAFKA_API_KEY" "KAFKA_API_SECRET" "SCHEMA_REGISTRY_URL" "SCHEMA_REGISTRY_API_KEY" "SCHEMA_REGISTRY_API_SECRET")
    MISSING_VARS=0
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=" .env; then
            print_status "$VAR configured"
        else
            print_error "$VAR missing in .env"
            MISSING_VARS=1
        fi
    done
    
    if [ $MISSING_VARS -eq 1 ]; then
        print_error "Some required variables are missing in .env"
        exit 1
    fi
else
    print_error ".env file not found"
    print_info "Terraform should have generated this file automatically"
    exit 1
fi

echo ""

# Display summary
echo -e "${BLUE}[6/6] Setup Complete!${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup completed successfully!                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
print_info "Next steps:"
echo "  1. Review the deployed resources in Confluent Cloud Console"
echo "  2. Run './scripts/test.sh' to produce test data"
echo "  3. Use Flink SQL queries in docs/TESTING.md to validate"
echo "  4. Run './scripts/cleanup.sh' when done to remove resources"
echo ""
print_warning "Important: Resources in Confluent Cloud will incur charges"
print_info "Remember to run cleanup.sh when you're done testing"
echo ""

# Display resource information
cd "$PROJECT_ROOT/terraform"
echo -e "${BLUE}Resource Information:${NC}"
echo ""
terraform output -json | python3 -c "
import json, sys
outputs = json.load(sys.stdin)
for key, value in outputs.items():
    if not value.get('sensitive', False):
        print(f'  {key}: {value[\"value\"]}')
    else:
        print(f'  {key}: <sensitive>')
"

echo ""
print_status "Setup script completed"

# Made with Bob
