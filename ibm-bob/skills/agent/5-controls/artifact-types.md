# Domain 5 — Controls: Artifact Types

> **ADK version**: 2.15.0 · All schemas verified live via `orchestrate controls get-type -v`

There are **13 artifact types** across 3 asset categories.

---

## Agent artifact types (5)

### `Guardrails` — Content Guardrails

**Applies to**: agent, tool  
**Purpose**: Enforce content safety. Detects jailbreak, HAP, harmful content, violence, sexual content, and social bias using an external guardrails detection service.

**Config schema** (all defaults `false`):

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled.sexual_content` | boolean | `false` | Detect sexual or explicit content |
| `enabled.violence` | boolean | `false` | Detect violent content |
| `enabled.hap` | boolean | `false` | Detect hate, abuse, and profanity |
| `enabled.harm` | boolean | `false` | Detect harmful content |
| `enabled.jailbreak` | boolean | `false` | Detect jailbreak attempts |
| `enabled.social_bias` | boolean | `false` | Detect social bias |
| `block_message` | string | `"Content blocked by guardrails controls"` | Message returned when content is blocked |

**Minimal example**:
```bash
orchestrate controls create \
  --artifact Guardrails \
  --name content-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 1 \
  --config '{"enabled":{"jailbreak":true,"hap":true,"harm":true},"block_message":"This content cannot be processed."}' \
  --agent "MyAgent"
```

> All detection categories are **opt-in** — nothing is blocked unless you explicitly set `true`.

---

### `pii_filter` — PII Filter

**Applies to**: agent only  
**Purpose**: Detect and mask personally identifiable information. Supports redact, partial, hash, tokenize, and remove strategies.

**Config schema**:

| Field | Type | Default | Description |
|---|---|---|---|
| `detect_ssn` | boolean | `false` | Social Security Numbers |
| `detect_bsn` | boolean | `false` | Dutch Burger Service Numbers |
| `detect_credit_card` | boolean | `false` | Credit card numbers |
| `detect_email` | boolean | `false` | Email addresses |
| `detect_phone` | boolean | `false` | Phone numbers |
| `detect_ip_address` | boolean | `false` | IP addresses |
| `detect_date_of_birth` | boolean | `false` | Dates of birth |
| `detect_passport` | boolean | `false` | Passport numbers |
| `detect_driver_license` | boolean | `false` | Driver license numbers |
| `detect_bank_account` | boolean | `false` | Bank account numbers |
| `detect_medical_record` | boolean | `false` | Medical record numbers |
| `default_mask_strategy` | enum | `"redact"` | `redact` / `partial` / `hash` / `tokenize` / `remove` |
| `redaction_text` | string | `"[REDACTED]"` | Replacement text when `redact` strategy is used |
| `block_on_detection` | boolean | `false` | Block entire request/response when PII is found |
| `log_detections` | boolean | `false` | Log all PII detections for audit |
| `include_detection_details` | boolean | `false` | Include detection metadata in response |
| `max_text_bytes` | integer | `10485760` | Maximum text size to process (10 MB) |
| `max_nested_depth` | integer | `32` | Max nesting depth for structured input |
| `max_collection_items` | integer | `4096` | Max items in a collection to process |
| `custom_patterns` | array[string] | `[]` | Custom regex patterns for additional PII types |
| `allowlist_patterns` | array[string] | `[]` | Values to exempt from detection |

**Minimal example** (live control from env):
```bash
orchestrate controls create \
  --artifact pii_filter \
  --name pii-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --config '{"detect_ssn":true,"detect_email":true,"detect_phone":true,"detect_credit_card":true,"detect_bank_account":true,"default_mask_strategy":"redact","redaction_text":"[REDACTED]","log_detections":true}' \
  --agent "test_DA"
```

**Mask strategy guide**:

| Strategy | Behaviour | Example |
|---|---|---|
| `redact` | Replace with `redaction_text` | `john@acme.com` → `[REDACTED]` |
| `partial` | Show partial value | `john@acme.com` → `j***@acme.com` |
| `hash` | SHA-256 hash | `john@acme.com` → `a94f...` |
| `tokenize` | Replace with stable token | `john@acme.com` → `TOKEN_001` |
| `remove` | Delete from text entirely | `john@acme.com` → `` |

---

### `SecretsDetection` — Secrets Detector

**Applies to**: agent, tool  
**Purpose**: Detect credentials and secrets (API keys, JWTs, private keys) in inputs/outputs with optional redaction or blocking.

**Config schema**:

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled.aws_access_key_id` | boolean | `false` | AWS Access Key IDs |
| `enabled.aws_secret_access_key` | boolean | `false` | AWS Secret Access Keys |
| `enabled.google_api_key` | boolean | `false` | Google API keys |
| `enabled.slack_token` | boolean | `false` | Slack tokens |
| `enabled.private_key_block` | boolean | `false` | PEM-style private key blocks |
| `enabled.jwt_like` | boolean | `false` | JWT-like tokens (3 base64 segments) |
| `enabled.hex_secret_32` | boolean | `false` | 32-character hex secrets |
| `enabled.base64_24` | boolean | `false` | Base64-encoded strings ≥ 24 characters |
| `redact` | boolean | `false` | Replace secrets with `redaction_text` |
| `redaction_text` | string | `"***REDACTED***"` | Replacement text |
| `block_on_detection` | boolean | **required** | Block when secrets detected |
| `min_findings_to_block` | integer | `1` | Min secrets to trigger block |

**Example**:
```bash
orchestrate controls create \
  --artifact SecretsDetection \
  --name secrets-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --config '{"enabled":{"aws_access_key_id":true,"jwt_like":true,"private_key_block":true},"redact":true,"block_on_detection":false}' \
  --agent "MyAgent"
```

> `block_on_detection` is **required** in the config schema.

---

### `RegexPattern` — Regex Pattern

**Applies to**: agent only  
**Purpose**: Match a custom regular expression and either redact or block matching content.

**Config schema**:

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `regex_patterns` | array[string] | ✅ | — | Array of regex patterns (at least 1) |
| `strategy` | enum | ✅ | `"block"` | `"redact"` or `"block"` |
| `redaction_text` | string | ❌ | `"[REDACTED]"` | Replacement when strategy is `redact` |

**Example** — block any mention of internal project codes:
```bash
orchestrate controls create \
  --artifact RegexPattern \
  --name internal-code-guard \
  --hook agent_post_invoke \
  --config '{"regex_patterns":["PROJ-[0-9]{4,}","INTERNAL-[A-Z]+"],"strategy":"redact","redaction_text":"[INTERNAL]"}' \
  --agent "MyAgent"
```

---

### `OutputLengthGuardPlugin` — Output Length Guard

**Applies to**: agent, tool  
**Purpose**: Enforce minimum and maximum output lengths in characters or tokens. Truncate or block oversized outputs.

**Config schema**:

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `limit_mode` | enum | ✅ | `"character"` | `"character"` or `"token"` |
| `strategy` | enum | ✅ | `"truncate"` | `"truncate"` or `"block"` |
| `min_chars` | integer | ❌ | `0` | Minimum characters (0 = disabled) |
| `max_chars` | integer | ❌ | `15000` | Maximum characters (0 = disabled) |
| `min_tokens` | integer | ❌ | `0` | Minimum tokens (0 = disabled) |
| `max_tokens` | integer/null | ❌ | `null` | Maximum tokens (null = disabled) |
| `chars_per_token` | integer | ❌ | `4` | Token estimation ratio |
| `ellipsis` | string | ❌ | `"…"` | Suffix appended when truncating |
| `word_boundary` | boolean | ❌ | `false` | Truncate at word boundaries |
| `max_text_length` | integer | ❌ | `1000000` | Security: max raw input size |
| `max_structure_size` | integer | ❌ | `10000` | Security: max items in list/dict |
| `max_recursion_depth` | integer | ❌ | `100` | Security: max nesting depth |

**Example**:
```bash
orchestrate controls create \
  --artifact OutputLengthGuardPlugin \
  --name output-length-guard \
  --hook agent_post_invoke \
  --config '{"limit_mode":"character","strategy":"truncate","max_chars":5000,"ellipsis":"... [truncated]","word_boundary":true}' \
  --agent "MyAgent"
```

---

## Tool artifact types (5)

> `Guardrails`, `OutputLengthGuardPlugin`, and `SecretsDetection` schemas are the same as agent types above.
> Use `tool_pre_invoke` or `tool_post_invoke` hooks when binding to tools.

### `SQLSanitizer` — SQL Sanitizer

**Applies to**: tool only  
**Purpose**: Detect and block risky SQL patterns to prevent SQL injection through tool arguments.

**Config schema**:

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `block_on_violation` | boolean | ✅ | `true` | Block when violation detected |
| `blocked_statements` | array[string] | ❌ | `["\bDROP\b","\bTRUNCATE\b","\bALTER\b","\bGRANT\b","\bREVOKE\b"]` | Regex patterns for blocked SQL statements |
| `block_delete_without_where` | boolean | ❌ | `true` | Block DELETE without WHERE |
| `block_update_without_where` | boolean | ❌ | `true` | Block UPDATE without WHERE |
| `strip_comments` | boolean | ❌ | `true` | Remove SQL comments |
| `require_parameterization` | boolean | ❌ | `false` | Require parameterized queries |

**Example**:
```bash
orchestrate controls create \
  --artifact SQLSanitizer \
  --name db-sql-guard \
  --hook tool_pre_invoke \
  --config '{"block_on_violation":true,"strip_comments":true,"block_delete_without_where":true,"block_update_without_where":true}' \
  --tool "my-db-tool"
```

---

### `RateLimiterPlugin` — Rate Limiter

**Applies to**: tool only  
**Purpose**: Enforce per-tool and per-tenant rate limits (requests per minute).

**Config schema**:

| Field | Type | Default | Description |
|---|---|---|---|
| `by_tool` | integer | `30` | Rate limit per tool per minute |
| `by_tenant` | integer | `3000` | Rate limit per tenant per minute |

**Example**:
```bash
orchestrate controls create \
  --artifact RateLimiterPlugin \
  --name api-rate-limit \
  --hook tool_pre_invoke \
  --config '{"by_tool":20,"by_tenant":500}' \
  --tool "external-api-tool"
```

---

## Model artifact types (3)

Model controls bind to **model names** (not agent names). They require `--model <model-name>`.

### `fallback` — Fallback

**Applies to**: model only  
**Purpose**: Route to a fallback model on specific HTTP error codes.

**Config schema** (root key: `fallBack`):
```json
{
  "fallBack": {
    "strategy": {
      "mode": "fallback",
      "on_status_codes": [429, 500, 502, 503, 504, 404]
    },
    "retry": {
      "attempts": 1,
      "on_status_codes": [429, 500, 502]
    },
    "targets": [
      {
        "provider": "watsonx",
        "override_params": { "model": "ibm/granite-3-8b-instruct" }
      }
    ]
  }
}
```

---

### `load_balance` — Load Balance

**Applies to**: model only  
**Purpose**: Weighted distribution of requests across multiple model providers.

**Config schema** (root key: `loadBalance`):
```json
{
  "loadBalance": {
    "strategy": { "mode": "loadbalance" },
    "retry": { "attempts": 1, "on_status_codes": [429, 500, 502] },
    "targets": [
      { "provider": "watsonx", "weight": 70, "override_params": { "model": "ibm/granite-3-8b-instruct" } },
      { "provider": "watsonx", "weight": 30, "override_params": { "model": "ibm/granite-3-3b-instruct" } }
    ]
  }
}
```

> `targets` requires **at least 2** items. Each `weight` is 0-100.

---

### `retry_mode` — Retry

**Applies to**: model only  
**Purpose**: Retry the same model up to 5 times on specific HTTP status codes.

**Config schema** (root key: `Retry` — capital R):
```json
{
  "Retry": {
    "strategy": { "mode": "single" },
    "retry": { "attempts": 3, "on_status_codes": [429, 500, 502] },
    "targets": [
      { "provider": "watsonx", "override_params": { "model": "ibm/granite-3-8b-instruct" } }
    ]
  }
}
```

> `targets` must have **exactly 1** item. `attempts` max is 5.
