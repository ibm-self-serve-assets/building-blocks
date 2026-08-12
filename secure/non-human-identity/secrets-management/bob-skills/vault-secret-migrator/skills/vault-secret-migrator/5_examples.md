# Vault Secret Migrator — Examples

Complete worked examples from scan to migration.

---

## Example 1 — Python Flask API

**Scenario:** Flask app with hardcoded database URL, Stripe key, SendGrid key, and JWT secret.

### Initial state (`src/config.py`)
```python
# Application Configuration
import os

DATABASE_URL = "postgresql://admin:MyP@ssw0rd123@localhost:5432/myapp"
STRIPE_SECRET_KEY = "sk_live_51H8x9y2eZvKYlo2C9UzF8x..."
SENDGRID_API_KEY = "SG.ngeVfQFYQlKU0ufo8x5d1A.TwL2iGABf9DHoTf..."
JWT_SECRET = "my-super-secret-jwt-key-12345"
DEBUG = True
```

### Step 1 — Scan
```python
grep(
  pattern="(?i)(api[_-]?key|apikey|secret[_-]?key|password|passwd)[\\s]*[=:]\\s*['\"]([^'\"]{8,})['\"]",
  path="src",
  include="*.py"
)
# Result: 4 matches in src/config.py — lines 4, 5, 6, 7
```

### Step 2 — Read full context
```python
read_file(path="src/config.py")
```

### Step 3 — Present findings and get confirmation
```
Findings in src/config.py:
  🔴 CRITICAL  Line 4  — PostgreSQL connection string (DATABASE_URL)
               Proposed Vault path: secret/myapp/production/database/credentials
  🟠 HIGH      Line 5  — Stripe secret key (STRIPE_SECRET_KEY)
               Proposed Vault path: secret/myapp/production/api/stripe
  🟠 HIGH      Line 6  — SendGrid API key (SENDGRID_API_KEY)
               Proposed Vault path: secret/myapp/production/api/sendgrid
  🔴 CRITICAL  Line 7  — JWT signing secret (JWT_SECRET)
               Proposed Vault path: secret/myapp/production/auth/jwt
```

```python
ask_followup_question(
  question="Found 4 hardcoded secrets in src/config.py. Proceed with migration?",
  suggestion_a="Yes, migrate all secrets to Vault",
  suggestion_b="Yes, but keep JWT_SECRET for now",
  suggestion_c="No, let me review first"
)
```

### Step 4 — Push to Vault
```python
mcp__vault__write_secret(mount="secret", path="myapp/production/database/credentials", key="url", value="postgresql://admin:MyP@ssw0rd123@localhost:5432/myapp")
mcp__vault__write_secret(mount="secret", path="myapp/production/api/stripe", key="secret_key", value="sk_live_51H8x9y2eZvKYlo2C9UzF8x...")
mcp__vault__write_secret(mount="secret", path="myapp/production/api/sendgrid", key="api_key", value="SG.ngeVfQFYQlKU0ufo8x5d1A...")
mcp__vault__write_secret(mount="secret", path="myapp/production/auth/jwt", key="secret", value="my-super-secret-jwt-key-12345")

# Verify each write
mcp__vault__read_secret(mount="secret", path="myapp/production/database/credentials")
```

### Step 5 — Replace hardcoded values (`apply_diff`)

**Final state (`src/config.py`):**
```python
# Application Configuration
import os
import hvac

# Vault client initialisation
vault_client = hvac.Client(
    url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
    token=os.environ["VAULT_TOKEN"]
)

# Database Configuration — retrieved from Vault
db_secret = vault_client.secrets.kv.v2.read_secret_version(
    path="myapp/production/database/credentials"
)["data"]["data"]
DATABASE_URL = db_secret["url"]

# API Keys — retrieved from Vault
stripe_secret = vault_client.secrets.kv.v2.read_secret_version(
    path="myapp/production/api/stripe"
)["data"]["data"]
STRIPE_SECRET_KEY = stripe_secret["secret_key"]

sendgrid_secret = vault_client.secrets.kv.v2.read_secret_version(
    path="myapp/production/api/sendgrid"
)["data"]["data"]
SENDGRID_API_KEY = sendgrid_secret["api_key"]

# JWT Configuration — retrieved from Vault
jwt_secret = vault_client.secrets.kv.v2.read_secret_version(
    path="myapp/production/auth/jwt"
)["data"]["data"]
JWT_SECRET = jwt_secret["secret"]

DEBUG = True
```

**Outcome:** 4 secrets migrated, code maintains same variable interface, no secrets in source.

---

## Example 2 — Node.js Microservice

**Scenario:** Node.js app with AWS credentials and multi-environment database passwords.

### Initial state
```javascript
// config/aws.js
module.exports = {
  accessKeyId: 'AKIAIOSFODNN7EXAMPLE',
  secretAccessKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  region: 'us-east-1'
};

// config/database.js
module.exports = {
  development: { password: 'dev_password_123' },
  production:  { password: 'Pr0d_P@ssw0rd_456!' }
};
```

### Scan
```python
grep(pattern="(AKIA|ASIA)[A-Z0-9]{16}", path="config", include="*.js")
grep(pattern="(?i)password[\\s]*[=:]\\s*['\"]([^'\"]{6,})['\"]", path="config", include="*.js")
```

### Push to Vault
```python
mcp__vault__write_secret(mount="secret", path="myapp/production/aws/credentials", key="access_key_id", value="AKIAIOSFODNN7EXAMPLE")
mcp__vault__write_secret(mount="secret", path="myapp/production/aws/credentials", key="secret_access_key", value="wJalrXUtnFEMI/...")
mcp__vault__write_secret(mount="secret", path="myapp/production/database/credentials", key="password", value="Pr0d_P@ssw0rd_456!")
mcp__vault__write_secret(mount="secret", path="myapp/development/database/credentials", key="password", value="dev_password_123")
```

### Final state
```javascript
const vault = require('node-vault')({
  endpoint: process.env.VAULT_ADDR || 'http://localhost:8200',
  token: process.env.VAULT_TOKEN
});

async function getDbConfig(environment) {
  const secret = await vault.read(
    `secret/data/myapp/${environment}/database/credentials`
  );
  return secret.data.data;
}

async function getAwsConfig() {
  const secret = await vault.read('secret/data/myapp/production/aws/credentials');
  return secret.data.data;
}

module.exports = { getDbConfig, getAwsConfig };
```

---

## Example 3 — Multi-Environment Pattern

```python
import os, hvac

def get_vault_client():
    return hvac.Client(url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"])

def get_environment():
    return os.environ.get("APP_ENV", "development")

def get_secret(path):
    client = get_vault_client()
    full_path = f"myapp/{get_environment()}/{path}"
    return client.secrets.kv.v2.read_secret_version(path=full_path)["data"]["data"]

# Usage — automatically selects dev / staging / production
DATABASE_URL = get_secret("database/credentials")["url"]
API_KEY      = get_secret("api/keys")["stripe_key"]
```

**Vault structure:**
```
secret/myapp/development/database/credentials
secret/myapp/development/api/keys
secret/myapp/staging/database/credentials
secret/myapp/staging/api/keys
secret/myapp/production/database/credentials
secret/myapp/production/api/keys
```

---

## Example 4 — CI/CD Pipeline (GitHub Actions)

**Before:**
```yaml
- name: Deploy
  env:
    DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

**After:**
```yaml
- name: Import secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: ${{ secrets.VAULT_ADDR }}
    token: ${{ secrets.VAULT_TOKEN }}
    secrets: |
      secret/data/myapp/production/database/credentials url | DATABASE_URL ;
      secret/data/myapp/production/api/keys stripe_key | API_KEY

- name: Deploy
  run: ./deploy.sh
```

---

## Example 5 — SSH Private Keys

```python
import hvac, tempfile, os

def get_ssh_key():
    """Retrieve SSH private key from Vault and write to a secure temp file."""
    vault_client = hvac.Client(url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"])
    secret = vault_client.secrets.kv.v2.read_secret_version(
        path="myapp/production/ssh/private-key"
    )
    key_content = secret["data"]["data"]["key"]

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem") as f:
        f.write(key_content)
        key_path = f.name

    os.chmod(key_path, 0o600)  # Restrictive permissions
    return key_path

key_path = get_ssh_key()
try:
    ssh_client.connect(hostname, key_filename=key_path)
finally:
    os.unlink(key_path)  # Always clean up
```

**Security rules for private keys:**
- Never log key content.
- Always set `0600` permissions on temp files.
- Delete temp files in a `finally` block.
- Consider Vault's SSH Secrets Engine for dynamic key generation.

---

## Common Code Patterns

### Lazy Initialisation
```python
class Config:
    _vault_client = None

    @classmethod
    def get_vault_client(cls):
        if cls._vault_client is None:
            cls._vault_client = hvac.Client(
                url=os.environ["VAULT_ADDR"],
                token=os.environ["VAULT_TOKEN"]
            )
        return cls._vault_client

    @classmethod
    def get_secret(cls, path):
        return cls.get_vault_client().secrets.kv.v2.read_secret_version(
            path=path
        )["data"]["data"]
```

### TTL Cache
```python
from datetime import datetime, timedelta
from functools import wraps

def cache_secret(ttl_seconds=300):
    cache = {}
    def decorator(func):
        @wraps(func)
        def wrapper(path):
            now = datetime.now()
            if path in cache:
                value, ts = cache[path]
                if now - ts < timedelta(seconds=ttl_seconds):
                    return value
            value = func(path)
            cache[path] = (value, now)
            return value
        return wrapper
    return decorator

@cache_secret(ttl_seconds=300)
def get_secret(path):
    return vault_client.secrets.kv.v2.read_secret_version(path=path)["data"]["data"]
```

### Graceful Fallback
```python
def get_secret(vault_path, env_var_name):
    """Try Vault first, fall back to environment variable."""
    try:
        secret = vault_client.secrets.kv.v2.read_secret_version(path=vault_path)
        return secret["data"]["data"]["value"]
    except Exception as e:
        logger.warning(f"Vault unavailable ({e}), falling back to {env_var_name}")
        return os.environ.get(env_var_name)
```
