# Vault Secret Migrator — Secret Detection Patterns

Comprehensive regex patterns for identifying hardcoded secrets. Use with `grep`.

---

## API Keys

### Generic API Key
```
(?i)(api[_-]?key|apikey|api[_-]?token)[\s]*[=:]\s*['"]([a-zA-Z0-9_\-]{20,})['"]
```
Examples: `API_KEY = "sk_live_51H8x9..."`, `apiKey: "AIzaSyD-..."`

### Stripe Keys *(High)*
```
(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}
```
Examples: `sk_live_51H8x9y2eZvKYlo2C...`, `pk_test_51H8x9y2...`

### SendGrid Keys *(High)*
```
SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}
```

### Twilio Keys *(High)*
```
SK[a-z0-9]{32}
```

### Mailgun Keys *(Medium)*
```
key-[a-zA-Z0-9]{32}
```

### Slack API Tokens *(High)*
```
xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}
```
Examples: `xoxb-1234567890-1234567890-abcdef...`

### Google API Keys *(High)*
```
AIza[0-9A-Za-z_-]{35}
```

---

## Cloud Credentials

### AWS Access Key ID *(Critical)*
```
(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}
```
Examples: `AKIAIOSFODNN7EXAMPLE`, `ASIATESTACCESSKEY123`

### AWS Secret Access Key *(Critical)*
```
(?i)aws[_-]?secret[_-]?access[_-]?key[\s]*[=:]\s*['"]([a-zA-Z0-9/+=]{40})['"]
```

### AWS Session Token *(High)*
```
(?i)aws[_-]?session[_-]?token[\s]*[=:]\s*['"]([a-zA-Z0-9/+=]{100,})['"]
```

### Azure Storage Connection String *(Critical)*
```
DefaultEndpointsProtocol=https;AccountName=[a-zA-Z0-9]+;AccountKey=[a-zA-Z0-9+/=]{88};EndpointSuffix=core\.windows\.net
```

### GCP Service Account JSON *(Critical)*
```
"type":\s*"service_account"
```
Context check: must be in a JSON structure that also contains a `private_key` field.

### GCP API Key *(High)*
```
(?i)gcp[_-]?api[_-]?key[\s]*[=:]\s*['"]([a-zA-Z0-9_-]{39})['"]
```

---

## Database Credentials

### PostgreSQL Connection String *(Critical)*
```
postgres(?:ql)?://[a-zA-Z0-9_-]+:[^@\s]+@[a-zA-Z0-9.-]+(?::\d+)?/[a-zA-Z0-9_-]+
```
Examples: `postgresql://user:pass@localhost:5432/db`

### MySQL Connection String *(Critical)*
```
mysql://[a-zA-Z0-9_-]+:[^@\s]+@[a-zA-Z0-9.-]+(?::\d+)?/[a-zA-Z0-9_-]+
```

### MongoDB Connection String *(Critical)*
```
mongodb(?:\+srv)?://[a-zA-Z0-9_-]+:[^@\s]+@[a-zA-Z0-9.-]+(?::\d+)?(?:/[a-zA-Z0-9_-]+)?
```
Examples: `mongodb://admin:pass@localhost:27017/db`, `mongodb+srv://user:pass@cluster.mongodb.net/db`

### Redis Connection String *(High)*
```
redis://:[^@\s]+@[a-zA-Z0-9.-]+(?::\d+)?
```

### Generic Database Password *(Critical)*
```
(?i)(db|database)[_-]?(password|passwd|pwd)[\s]*[=:]\s*['"]([^'"]{8,})['"]
```

---

## Authentication Tokens

### GitHub Personal Access Token *(High)*
```
gh[pousr]_[A-Za-z0-9_]{36,}
```
Examples: `ghp_16C7e42F292c6912E7710c...`

### GitLab Personal Access Token *(High)*
```
glpat-[a-zA-Z0-9_-]{20}
```

### JWT Secret *(Critical)*
```
(?i)jwt[_-]?secret[\s]*[=:]\s*['"]([a-zA-Z0-9_-]{32,})['"]
```

### OAuth Client Secret *(High)*
```
(?i)(oauth|client)[_-]?secret[\s]*[=:]\s*['"]([a-zA-Z0-9_-]{20,})['"]
```

### Bearer Token *(High)*
```
(?i)bearer[\s]+[a-zA-Z0-9_\-\.=]{20,}
```

---

## Private Keys

### RSA Private Key *(Critical)*
```
-----BEGIN RSA PRIVATE KEY-----
```

### OpenSSH Private Key *(Critical)*
```
-----BEGIN OPENSSH PRIVATE KEY-----
```

### EC Private Key *(Critical)*
```
-----BEGIN EC PRIVATE KEY-----
```

### PGP Private Key *(Critical)*
```
-----BEGIN PGP PRIVATE KEY BLOCK-----
```

### Generic Encryption Key *(High)*
```
(?i)(encryption|encrypt)[_-]?key[\s]*[=:]\s*['"]([a-zA-Z0-9+/=]{32,})['"]
```

---

## Generic Passwords

### Password Variable *(High)*
```
(?i)(password|passwd|pwd)[\s]*[=:]\s*['"]([^'"]{8,})['"]
```
Exclude placeholders: `"password"`, `"changeme"`, `"your-password-here"`.

### Admin/Root Password *(Critical)*
```
(?i)(admin|root)[_-]?(password|passwd|pwd)[\s]*[=:]\s*['"]([^'"]{6,})['"]
```

### Generic Secret Key *(High)*
```
(?i)secret[_-]?key[\s]*[=:]\s*['"]([a-zA-Z0-9_\-+/=]{20,})['"]
```

---

## Service-Specific

### Slack Webhook URL *(Medium)*
```
https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}
```

### Discord Webhook URL *(Medium)*
```
https://discord(?:app)?\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+
```

### NPM Token *(High)*
```
npm_[a-zA-Z0-9]{36}
```

### PyPI Token *(High)*
```
pypi-AgEIcHlwaS5vcmc[a-zA-Z0-9_-]{70,}
```

---

## Detection Strategies

### Regex Scanning
Apply each pattern above using `grep`. Capture the file path, line number, and matched value.

### Entropy Analysis
Flag strings with Shannon entropy > 4.5 and length ≥ 20 characters as potential secrets, then cross-check with context.

### Context Analysis
For each match, check:
- Variable name (contains `key`, `secret`, `password`, `token`?)
- Is it a direct assignment or an environment variable reference?
- Is it marked as an example or placeholder in a comment?
- Is it in a test file vs production code?

### File Type Prioritisation

| Priority | File types |
|----------|-----------|
| High | `.env`, `.env.*`, `config.*`, `secrets.*`, `credentials.*` |
| Medium | `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php` |
| Low | `.md`, `.txt`, `.rst`, `.html` |
| Exclude | `.git/`, `node_modules/`, `venv/`, `__pycache__/` |

---

## False Positive Reduction

**Common placeholder values to exclude:**
`your-api-key-here`, `changeme`, `password`, `secret`, `example`, `test`, `dummy`, `fake`, `sample`, `xxx`, `000`

**Exclude environment variable references:**
```python
os.environ.get("SECRET_KEY")   # Python
process.env.API_KEY             # Node.js
System.getenv("PASSWORD")       # Java
${SECRET_KEY}                   # Shell/config templates
```

**Exclude commented-out examples** — check surrounding lines for indicators: `"example"`, `"placeholder"`, `"replace with"`, `"TODO"`.

---

## Finding Report Format

Each finding should include:

| Field | Description |
|-------|-------------|
| `severity` | `critical` \| `high` \| `medium` \| `low` |
| `type` | e.g. "AWS Access Key", "Database Password" |
| `file_path` | Relative path to file |
| `line_number` | Line number |
| `matched_pattern` | Which pattern matched |
| `context` | Surrounding 3–5 lines |
| `masked_value` | `AKIA****` (first 4 chars + `****`) |
| `proposed_vault_path` | e.g. `secret/myapp/production/aws/access-key-id` |
| `confidence` | `high` \| `medium` \| `low` |
