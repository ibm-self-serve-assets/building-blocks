"""
Secret Detection Patterns
Comprehensive patterns for detecting 40+ types of hardcoded secrets
"""

import re

# Secret detection patterns with descriptions
SECRET_PATTERNS = {
    # AWS Secrets
    'aws_access_key_id': {
        'pattern': r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
        'description': 'AWS Access Key ID'
    },
    'aws_secret_access_key': {
        'pattern': r'(?i)aws(.{0,20})?(?:secret)(.{0,20})?[\'"][0-9a-zA-Z/+=]{40}[\'"]',
        'description': 'AWS Secret Access Key'
    },
    'aws_session_token': {
        'pattern': r'(?i)aws(.{0,20})?(?:session|token)(.{0,20})?[\'"][0-9a-zA-Z/+=]{100,}[\'"]',
        'description': 'AWS Session Token'
    },

    # Google Cloud Platform
    'gcp_service_account': {
        'pattern': r'"type":\s*"service_account"',
        'description': 'GCP Service Account Key'
    },
    'gcp_api_key': {
        'pattern': r'AIza[0-9A-Za-z\\-_]{35}',
        'description': 'Google API Key'
    },
    'gcp_oauth_token': {
        'pattern': r'ya29\.[0-9A-Za-z\-_]+',
        'description': 'Google OAuth Access Token'
    },

    # Azure
    'azure_storage_key': {
        'pattern': r'(?i)azure(.{0,20})?[\'"][0-9a-zA-Z/+=]{88}[\'"]',
        'description': 'Azure Storage Account Key'
    },
    'azure_sas_token': {
        'pattern': r'(?i)sig=[a-zA-Z0-9%]{43,53}%3D',
        'description': 'Azure SAS Token'
    },
    'azure_client_secret': {
        'pattern': r'(?i)azure(.{0,20})?(?:client|secret)(.{0,20})?[\'"][0-9a-zA-Z\-_~]{34,40}[\'"]',
        'description': 'Azure Client Secret'
    },

    # GitHub
    'github_pat': {
        'pattern': r'ghp_[0-9a-zA-Z]{36}',
        'description': 'GitHub Personal Access Token'
    },
    'github_oauth': {
        'pattern': r'gho_[0-9a-zA-Z]{36}',
        'description': 'GitHub OAuth Access Token'
    },
    'github_app_token': {
        'pattern': r'(?:ghu|ghs)_[0-9a-zA-Z]{36}',
        'description': 'GitHub App Token'
    },

    # GitLab
    'gitlab_pat': {
        'pattern': r'glpat-[0-9a-zA-Z\-_]{20}',
        'description': 'GitLab Personal Access Token'
    },

    # Slack
    'slack_token': {
        'pattern': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[0-9a-zA-Z]{24,32}',
        'description': 'Slack Token'
    },
    'slack_webhook': {
        'pattern': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}',
        'description': 'Slack Webhook URL'
    },

    # Stripe
    'stripe_secret_key': {
        'pattern': r'sk_live_[0-9a-zA-Z]{24,}',
        'description': 'Stripe Secret Key'
    },
    'stripe_publishable_key': {
        'pattern': r'pk_live_[0-9a-zA-Z]{24,}',
        'description': 'Stripe Publishable Key'
    },

    # Twilio
    'twilio_account_sid': {
        'pattern': r'AC[a-z0-9]{32}',
        'description': 'Twilio Account SID'
    },
    'twilio_auth_token': {
        'pattern': r'(?i)twilio(.{0,20})?[\'"][0-9a-f]{32}[\'"]',
        'description': 'Twilio Auth Token'
    },

    # SendGrid
    'sendgrid_api_key': {
        'pattern': r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
        'description': 'SendGrid API Key'
    },

    # Mailgun
    'mailgun_api_key': {
        'pattern': r'key-[0-9a-zA-Z]{32}',
        'description': 'Mailgun API Key'
    },

    # Private Keys
    'rsa_private_key': {
        'pattern': r'-----BEGIN RSA PRIVATE KEY-----',
        'description': 'RSA Private Key'
    },
    'ec_private_key': {
        'pattern': r'-----BEGIN EC PRIVATE KEY-----',
        'description': 'EC Private Key'
    },
    'openssh_private_key': {
        'pattern': r'-----BEGIN OPENSSH PRIVATE KEY-----',
        'description': 'OpenSSH Private Key'
    },
    'pgp_private_key': {
        'pattern': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        'description': 'PGP Private Key'
    },
    'generic_private_key': {
        'pattern': r'-----BEGIN PRIVATE KEY-----',
        'description': 'Generic Private Key'
    },

    # Database Connection Strings
    'mysql_connection': {
        'pattern': r'mysql://[a-zA-Z0-9_]+:[a-zA-Z0-9_!@#$%^&*()]+@[a-zA-Z0-9.-]+:[0-9]+/[a-zA-Z0-9_]+',
        'description': 'MySQL Connection String'
    },
    'postgresql_connection': {
        'pattern': r'postgres(?:ql)?://[a-zA-Z0-9_]+:[a-zA-Z0-9_!@#$%^&*()]+@[a-zA-Z0-9.-]+:[0-9]+/[a-zA-Z0-9_]+',
        'description': 'PostgreSQL Connection String'
    },
    'mongodb_connection': {
        'pattern': r'mongodb(?:\+srv)?://[a-zA-Z0-9_]+:[a-zA-Z0-9_!@#$%^&*()]+@[a-zA-Z0-9.-]+(?::[0-9]+)?/[a-zA-Z0-9_]+',
        'description': 'MongoDB Connection String'
    },
    'redis_connection': {
        'pattern': r'redis://[a-zA-Z0-9_]*:?[a-zA-Z0-9_!@#$%^&*()]*@[a-zA-Z0-9.-]+:[0-9]+',
        'description': 'Redis Connection String'
    },
    'jdbc_url': {
        'pattern': r'jdbc:[a-z]+://[a-zA-Z0-9_]+:[a-zA-Z0-9_!@#$%^&*()]+@[a-zA-Z0-9.-]+:[0-9]+',
        'description': 'JDBC Connection URL'
    },

    # JWT Tokens
    'jwt_token': {
        'pattern': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'description': 'JSON Web Token (JWT)'
    },

    # Vault Tokens
    'vault_token': {
        'pattern': r'hvs\.[a-zA-Z0-9_-]{24,}',
        'description': 'HashiCorp Vault Token'
    },
    'vault_root_token': {
        'pattern': r's\.[a-zA-Z0-9]{24}',
        'description': 'HashiCorp Vault Root Token'
    },

    # Generic Patterns
    'generic_api_key': {
        'pattern': r'(?i)(?:api[_-]?key|apikey)[\s]*[=:]\s*[\'"]?[a-zA-Z0-9_\-]{20,}[\'"]?',
        'description': 'Generic API Key'
    },
    'generic_secret': {
        'pattern': r'(?i)(?:secret|token)[\s]*[=:]\s*[\'"]?[a-zA-Z0-9_\-]{20,}[\'"]?',
        'description': 'Generic Secret or Token'
    },
    'generic_password': {
        'pattern': r'(?i)(?:password|passwd|pwd)[\s]*[=:]\s*[\'"]?[a-zA-Z0-9_!@#$%^&*()]{8,}[\'"]?',
        'description': 'Generic Password'
    },

    # High Entropy Strings (Base64)
    'high_entropy_string': {
        'pattern': r'[\'"][a-zA-Z0-9+/]{32,}={0,2}[\'"]',
        'description': 'High Entropy String (Possible Base64 Secret)'
    },

    # Database URLs
    'database_url': {
        'pattern': r'(?i)(?:database|db)_url[\s]*[=:]\s*[\'"]?[a-z]+://[^\s\'"]+[\'"]?',
        'description': 'Database URL'
    }
}


def get_severity(pattern_name: str) -> str:
    """
    Determine severity level based on pattern type
    
    Args:
        pattern_name: Name of the detected pattern
        
    Returns:
        str: Severity level (critical, high, medium, low)
    """
    critical_patterns = [
        'aws_secret_access_key', 'aws_session_token',
        'azure_client_secret', 'azure_storage_key',
        'rsa_private_key', 'ec_private_key', 'openssh_private_key',
        'pgp_private_key', 'generic_private_key',
        'vault_root_token', 'stripe_secret_key',
        'database_url', 'mysql_connection', 'postgresql_connection',
        'mongodb_connection', 'jdbc_url'
    ]
    
    high_patterns = [
        'aws_access_key_id', 'gcp_service_account', 'gcp_api_key',
        'github_pat', 'github_oauth', 'gitlab_pat',
        'slack_token', 'twilio_auth_token',
        'sendgrid_api_key', 'mailgun_api_key',
        'vault_token', 'jwt_token',
        'generic_password', 'generic_secret'
    ]
    
    medium_patterns = [
        'azure_sas_token', 'github_app_token',
        'slack_webhook', 'stripe_publishable_key',
        'twilio_account_sid', 'generic_api_key',
        'redis_connection', 'high_entropy_string'
    ]
    
    if pattern_name in critical_patterns:
        return 'critical'
    elif pattern_name in high_patterns:
        return 'high'
    elif pattern_name in medium_patterns:
        return 'medium'
    else:
        return 'low'


def validate_pattern(pattern_name: str, value: str) -> bool:
    """
    Validate if a detected value matches additional criteria
    
    Args:
        pattern_name: Name of the pattern
        value: Detected value
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Additional validation logic can be added here
    # For example, checking length, format, etc.
    
    # Minimum length checks
    min_lengths = {
        'aws_access_key_id': 20,
        'aws_secret_access_key': 40,
        'generic_api_key': 20,
        'generic_secret': 20,
        'generic_password': 8
    }
    
    if pattern_name in min_lengths:
        return len(value) >= min_lengths[pattern_name]
    
    return True

# Made with Bob
