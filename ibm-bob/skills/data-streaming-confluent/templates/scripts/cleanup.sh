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

echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║   Confluent Cloud Resource Cleanup                        ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

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

# Warning message
echo -e "${RED}⚠ WARNING ⚠${NC}"
echo ""
print_warning "This will DESTROY all resources created by Terraform:"
echo "  - Confluent Cloud environment"
echo "  - Kafka cluster"
echo "  - Flink compute pool"
echo "  - All topics and data"
echo "  - Service accounts and API keys"
echo ""
print_warning "This action CANNOT be undone!"
echo ""

# Confirmation
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_info "Cleanup cancelled"
    exit 0
fi

echo ""
print_warning "Last chance! Type 'DELETE' to proceed:"
read -p "> " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "DELETE" ]; then
    print_info "Cleanup cancelled"
    exit 0
fi

echo ""

# Check if Terraform directory exists
if [ ! -d "$PROJECT_ROOT/terraform" ]; then
    print_error "Terraform directory not found"
    exit 1
fi

cd "$PROJECT_ROOT/terraform"

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    print_warning "Terraform not initialized"
    print_info "Initializing Terraform..."
    terraform init
fi

echo ""
echo -e "${BLUE}[1/3] Planning Destruction...${NC}"
echo ""

print_info "Running terraform plan -destroy..."
if terraform plan -destroy -out=destroy.tfplan; then
    print_status "Destruction plan created"
else
    print_error "Failed to create destruction plan"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/3] Destroying Resources...${NC}"
echo ""

print_info "Running terraform apply destroy.tfplan..."
print_warning "This may take several minutes..."
echo ""

if terraform apply destroy.tfplan; then
    print_status "Resources destroyed successfully"
    rm -f destroy.tfplan
else
    print_error "Failed to destroy resources"
    print_info "Some resources may still exist in Confluent Cloud"
    print_info "Check Confluent Cloud Console and manually delete if needed"
    rm -f destroy.tfplan
    exit 1
fi

echo ""
echo -e "${BLUE}[3/3] Cleaning Up Local Files...${NC}"
echo ""

# Clean up Terraform state files
if [ -f "terraform.tfstate" ]; then
    print_info "Removing terraform.tfstate..."
    rm -f terraform.tfstate
    print_status "Removed terraform.tfstate"
fi

if [ -f "terraform.tfstate.backup" ]; then
    print_info "Removing terraform.tfstate.backup..."
    rm -f terraform.tfstate.backup
    print_status "Removed terraform.tfstate.backup"
fi

# Clean up .env file
if [ -f "$PROJECT_ROOT/python/.env" ]; then
    print_info "Removing python/.env..."
    rm -f "$PROJECT_ROOT/python/.env"
    print_status "Removed python/.env"
fi

# Optional: Clean up Python virtual environment
echo ""
read -p "Remove Python virtual environment? (yes/no): " REMOVE_VENV

if [ "$REMOVE_VENV" = "yes" ]; then
    if [ -d "$PROJECT_ROOT/python/venv" ]; then
        print_info "Removing Python virtual environment..."
        rm -rf "$PROJECT_ROOT/python/venv"
        print_status "Removed Python virtual environment"
    fi
fi

# Optional: Clean up Terraform plugins
echo ""
read -p "Remove Terraform plugins (.terraform directory)? (yes/no): " REMOVE_TERRAFORM

if [ "$REMOVE_TERRAFORM" = "yes" ]; then
    if [ -d ".terraform" ]; then
        print_info "Removing .terraform directory..."
        rm -rf .terraform
        print_status "Removed .terraform directory"
    fi
    if [ -f ".terraform.lock.hcl" ]; then
        print_info "Removing .terraform.lock.hcl..."
        rm -f .terraform.lock.hcl
        print_status "Removed .terraform.lock.hcl"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Cleanup completed successfully!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
print_status "All Confluent Cloud resources have been destroyed"
print_status "Local state files have been cleaned up"
echo ""
print_info "Verification steps:"
echo "  1. Log in to Confluent Cloud Console"
echo "  2. Verify the environment has been deleted"
echo "  3. Check your billing to ensure no resources are running"
echo ""
print_warning "If you see any remaining resources in Confluent Cloud:"
echo "  - Manually delete them through the Console"
echo "  - Contact Confluent Support if needed"
echo ""
print_info "To redeploy, run './scripts/setup.sh'"
echo ""

# Made with Bob
