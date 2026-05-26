# Automated Hardcoded Secret Detection and Vault Migration

A comprehensive solution for detecting hardcoded secrets in source code, encrypting them with HashiCorp Vault Transit engine, storing them securely in Vault KV, and automatically refactoring code to use Vault API calls.

## 🎯 Features

- **Automated Secret Detection**: Scans source code for 40+ types of hardcoded secrets
- **Transit Encryption**: Encrypts sensitive secrets using Vault Transit engine (AES256-GCM96)
- **Secure Storage**: Stores encrypted secrets in Vault KV v2 with metadata
- **Code Refactoring**: Automatically replaces hardcoded secrets with Vault API calls
- **Multi-Language Support**: Generates code examples in Python, Node.js, Go, CLI, and cURL
- **Production-Ready**: Complete Ansible deployment automation for Vault
- **Interactive UI**: Python Dash web application with professional IBM Carbon Design

## 📋 Architecture

```
├── ansible/                    # Vault deployment automation
│   ├── inventory/             # Server inventory
│   ├── roles/vault/           # Vault installation role
│   └── site.yml               # Main playbook
├── secret_scanner_app/        # Python Dash application
│   ├── app.py                 # Main application
│   ├── vault_client.py        # Vault API wrapper
│   ├── secret_patterns.py     # Detection patterns
│   ├── code_refactor.py       # Code refactoring engine
│   └── assets/                # Static files
└── docs/                      # Documentation
```

## 🚀 Quick Start

### 1. Deploy Vault with Ansible

```bash
cd ansible
# Configure inventory
vim inventory/hosts.ini
# Run deployment
ansible-playbook site.yml
```

### 2. Start Secret Scanner Application

```bash
cd secret_scanner_app
# Configure environment
cp .env.example .env
vim .env  # Set VAULT_ADDR and VAULT_TOKEN
# Start application
./start.sh
```

### 3. Access Application

Open http://localhost:8050 in your browser.

## 🔧 Requirements

- Python 3.9+
- Ansible 2.9+
- HashiCorp Vault 1.12+
- Linux/macOS (Windows supported via WSL)

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Security Best Practices](docs/SECURITY.md)

## 🔐 Security Features

- Transit encryption for sensitive secrets
- No secrets in logs or error messages
- Secure token management
- Audit logging support
- TLS support for production

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Support

For issues and questions, please open a GitHub issue.
