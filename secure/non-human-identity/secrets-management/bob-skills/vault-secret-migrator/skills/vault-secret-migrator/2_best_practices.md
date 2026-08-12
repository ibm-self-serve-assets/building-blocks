# Vault Secret Migrator — Best Practices

---

## Secret Detection Principles

### Comprehensive Scanning *(Critical)*
- Scan source code, configuration files, documentation, test files.
- Include CI/CD files (`.github/`, `.gitlab-ci.yml`), Dockerfiles, `docker-compose.yml`.
- Cover infrastructure-as-code files (Terraform, CloudFormation).
- Examine shell scripts and automation files.

### Context-Aware Detection *(High)*
- Check if the value is a comment placeholder (e.g. `"your-api-key-here"`) — not a real secret.
- Verify if already a reference to external storage (`os.environ.get(...)`, `process.env.*`).
- Distinguish test/mock values from production secrets.
- Consider naming conventions: variables prefixed `EXAMPLE_`, `TEST_`, `FAKE_` are low priority.

### Severity Classification *(High)*

| Level | Examples |
|-------|---------|
| Critical | Production DB credentials, cloud root/admin credentials, production private keys, write-access API keys |
| High | Stripe/SendGrid keys, OAuth secrets, JWT signing keys, encryption keys |
| Medium | Read-only API tokens, dev/staging credentials, limited-scope tokens |
| Low | Test credentials, documentation examples, expired/revoked credentials |

---

## Vault Integration Best Practices

### Logical Path Structure *(Critical)*
```
secret/[project]/[environment]/[service]/[secret-name]

secret/myapp/production/database/password
secret/myapp/production/api/stripe-secret-key
secret/myapp/staging/aws/access-key-id
secret/myapp/development/oauth/client-secret
```

### Secret Versioning *(Critical)*
- Enable versioning on all secret paths.
- Keep at least 3–5 versions for rollback capability.
- Use version pinning in critical applications.

### Access Control Policies *(High)*
- Create separate policies per environment (`prod`, `staging`, `dev`).
- Grant read-only access by default; limit write access to CI/CD and admin roles.
- Use path-based restrictions for service isolation.

Example HCL policy:
```hcl
# Application — read only
path "secret/data/myapp/production/*" {
  capabilities = ["read", "list"]
}

# CI/CD pipeline — read + write
path "secret/data/myapp/production/*" {
  capabilities = ["create", "read", "update", "list"]
}
```

### Authentication Methods *(High)*

| Context | Method |
|---------|--------|
| Local development | Token authentication |
| CI/CD pipelines | AppRole (role_id + secret_id) |
| Kubernetes | Kubernetes service account auth |
| Cloud VMs | Cloud provider identity (AWS IAM, Azure MSI, GCP SA) |

---

## Code Replacement Best Practices

### Maintain Code Functionality *(Critical)*
- Preserve variable names and types after replacement.
- Keep the same initialisation order.
- Maintain existing error handling behaviour.

```python
# Before
DATABASE_URL = "postgresql://user:pass@localhost/db"

# After — same interface, different source
DATABASE_URL = vault_client.read("secret/myapp/prod/db/url")["data"]["value"]
```

### Error Handling *(High)*

```python
# Vault connection failure — fail fast
try:
    vault_client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    if not vault_client.is_authenticated():
        raise RuntimeError("Failed to authenticate with Vault")
except Exception as e:
    logger.error(f"Vault connection failed: {e}")
    raise SystemExit("Cannot start application without Vault access")

# Secret not found — helpful error
secret = vault_client.read(secret_path)
if not secret:
    raise KeyError(f"Secret not found at {secret_path}")

# Permission denied — policy guidance
except hvac.exceptions.Forbidden:
    logger.error(f"Permission denied for {secret_path}. Check Vault policies.")
    raise
```

### Secret Caching *(High)*
- Cache secrets in memory only — never on disk.
- Set TTL based on rotation frequency (default: 300 seconds).
- Clear cache on application shutdown.

```python
class VaultSecretCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, path):
        if path in self.cache:
            value, timestamp = self.cache[path]
            if datetime.now() - timestamp < self.ttl:
                return value
        value = vault_client.read(path)
        self.cache[path] = (value, datetime.now())
        return value
```

### Logging Without Exposing Secrets *(Medium)*

```python
# ✅ Good
logger.info(f"Retrieved secret from {secret_path}")
logger.debug(f"Secret key: {key[:4]}****")

# ❌ Never do this
logger.info(f"API Key: {api_key}")
logger.error(f"Failed with secret: {secret}")
```

---

## Security Considerations

### Never Commit Secrets to Version Control *(Critical)*
Add to `.gitignore`:
```
.env
.env.*
!.env.example
secrets.yaml
secrets.json
*secret*
*credential*
*.pem
*.key
*.p12
*.pfx
```

Also: use `git-secrets` or `pre-commit` hooks; scan git history; rotate any secrets that were committed.

### Secret Rotation *(Critical)*
- Rotate all secrets **immediately** after migration.
- Establish a rotation schedule: 30–90 days for most secrets.
- Automate rotation where possible.
- Test rotation in non-production first.

### Audit Logging *(High)*
- Enable Vault audit logging.
- Monitor for unusual access patterns and failed auth attempts.
- Retain logs per compliance requirements.

### Backup and Disaster Recovery *(High)*
- Regular automated backups of Vault data, encrypted at rest.
- Store backups in a separate, secure location.
- Test restore procedures regularly.

---

## Migration Best Practices

### Phased Approach *(Critical)*
1. **Development** — Test migration with dev secrets.
2. **Staging** — Validate with staging secrets and full testing.
3. **Production** — Migrate with rollback plan in place.

### Rollback Checklist *(High)*
- [ ] Original code preserved in version control
- [ ] All Vault paths and mappings documented
- [ ] Rollback procedure tested before production migration
- [ ] Emergency access to original secrets available

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Incomplete detection — missing secrets in non-obvious locations | Scan all file types; check git history; cover IaC and CI/CD files |
| Breaking application startup due to Vault unavailability | Implement health checks; add clear startup error messages; test in isolation |
| Performance degradation from too many Vault calls | Cache secrets at startup; batch retrieval; load once, not per-request |
| Overly permissive Vault access | Principle of least privilege; environment-specific policies; regular audits |

---

## Quality Checklist

**Before migration:**
- [ ] All secrets identified and categorised
- [ ] Vault server accessible and configured
- [ ] Authentication method chosen and tested
- [ ] Vault path structure designed
- [ ] Team notified of migration plan
- [ ] Rollback procedure documented

**During migration:**
- [ ] Secrets pushed to Vault successfully
- [ ] Code changes maintain functionality
- [ ] Error handling implemented
- [ ] Logging configured (paths only, no values)

**After migration:**
- [ ] All hardcoded secrets removed
- [ ] Application tested thoroughly
- [ ] Documentation updated
- [ ] Team trained on new processes
- [ ] Monitoring and alerting configured
- [ ] Secret rotation schedule established
