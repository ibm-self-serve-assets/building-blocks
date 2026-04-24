#!/bin/bash

# Ansible Vault Deployment Script

echo "=========================================="
echo "HashiCorp Vault Deployment with Ansible"
echo "=========================================="
echo ""

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "Error: Ansible is not installed"
    echo "Please install Ansible first:"
    echo "  Ubuntu/Debian: sudo apt install ansible"
    echo "  RHEL/CentOS: sudo yum install ansible"
    echo "  macOS: brew install ansible"
    exit 1
fi

# Check if inventory file exists
if [ ! -f "inventory/hosts.ini" ]; then
    echo "Error: inventory/hosts.ini not found"
    echo "Please create and configure inventory/hosts.ini first"
    exit 1
fi

# Display inventory
echo "Target servers:"
ansible-inventory -i inventory/hosts.ini --list -y | grep ansible_host || echo "  localhost (local deployment)"
echo ""

# Confirm deployment
read -p "Do you want to proceed with Vault deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Starting Vault deployment..."
echo ""

# Run the playbook
ansible-playbook -i inventory/hosts.ini site.yml

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Vault Deployment Completed Successfully!"
    echo "=========================================="
    echo ""
    echo "IMPORTANT: Next Steps"
    echo "1. Retrieve initialization data from /etc/vault.d/vault-init.json on the Vault server"
    echo "2. Save unseal keys and root token securely"
    echo "3. Remove vault-init.json from the server"
    echo "4. Export environment variables:"
    echo "   export VAULT_ADDR=http://<vault-server-ip>:8200"
    echo "   export VAULT_TOKEN=<root-token>"
    echo "5. Verify: vault status"
    echo ""
else
    echo ""
    echo "Deployment failed. Please check the error messages above."
    exit 1
fi

# Made with Bob
