---
name: backend-development
description: Build Flask-based REST APIs with HashiCorp Vault integration, secret scanning, and Git repository analysis
---

Build Flask REST APIs with Vault integration:

<Steps>
<Step>
Setup Flask with CORS and proper error handling
</Step>
<Step>
Implement Vault client for encryption and secret storage
</Step>
<Step>
Create secret scanning with pattern-based detection (40+ patterns)
</Step>
<Step>
Build Git repository scanner for remote and local repos
</Step>
<Step>
Add comprehensive error handling with try-except blocks
</Step>
<Step>
Implement logging with RotatingFileHandler
</Step>
<Step>
Write tests for all endpoints
</Step>
<Step>
Deploy with environment configuration
</Step>
</Steps>

**Key Resources:**
- `api-patterns.md` - RESTful endpoint patterns, error handling, Vault client

**Essential Patterns:**
- RESTful endpoints: GET /api/resources, POST /api/resources, etc.
- Error handling: Try-except with proper status codes (400, 500)
- Vault operations: `VaultClient.encrypt()`, `VaultClient.store_secret()`
- Input validation: Check required fields before processing
- Logging: Use `app.logger.info()` and `app.logger.error()`

**Common Issues:**
- CORS errors: `CORS(app, resources={r"/api/*": {"origins": "*"}})`
- Port in use: Check with `netstat -tlnp | grep 3001`
- Import errors: Activate venv with `source venv/bin/activate`
- Vault timeout: Increase timeout `hvac.Client(url=addr, timeout=30)`