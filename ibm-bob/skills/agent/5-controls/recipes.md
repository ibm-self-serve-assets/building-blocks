# Domain 5 — Controls: Recipes

> **ADK version**: 2.15.0 · Copy-paste patterns for the most common scenarios

---

## Recipe 1 — Full PII protection on an agent

Redact SSN, email, phone, credit card, and bank account numbers on both input and output.
Uses the `test_DA` agent from the live `ibm_cloud` env.

```bash
orchestrate controls create \
  --artifact pii_filter \
  --name test-da-pii-full \
  --display-name "PII Full Guard — test_DA" \
  --description "Redacts SSN, email, phone, credit card, and bank account on all agent I/O" \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 50 \
  --config '{
    "detect_ssn": true,
    "detect_email": true,
    "detect_phone": true,
    "detect_credit_card": true,
    "detect_bank_account": true,
    "default_mask_strategy": "redact",
    "redaction_text": "[REDACTED]",
    "log_detections": true
  }' \
  --agent "test_DA"
```

**Verify**:
```bash
orchestrate controls get-details -n test-da-pii-full -v
```

---

## Recipe 2 — Content safety guardrail (jailbreak + HAP + harm)

Block jailbreak attempts, hate/abuse/profanity, and harmful content before the LLM sees them.
Run at priority 1 so it fires before any redaction controls.

```bash
orchestrate controls create \
  --artifact Guardrails \
  --name safety-guard \
  --display-name "Content Safety Guard" \
  --description "Blocks jailbreak, HAP, and harmful content" \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 1 \
  --config '{
    "enabled": {
      "jailbreak": true,
      "hap": true,
      "harm": true,
      "violence": false,
      "sexual_content": false,
      "social_bias": false
    },
    "block_message": "This request cannot be processed due to content policy."
  }' \
  --agent "test_DA"
```

---

## Recipe 3 — Full content safety (all categories)

Enable every guardrail category for maximum protection.

```bash
orchestrate controls create \
  --artifact Guardrails \
  --name full-safety-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 1 \
  --config '{
    "enabled": {
      "jailbreak": true,
      "hap": true,
      "harm": true,
      "violence": true,
      "sexual_content": true,
      "social_bias": true
    },
    "block_message": "Content blocked by safety policy."
  }' \
  --agent "MyAgent"
```

---

## Recipe 4 — Secrets detection (redact mode)

Detect and redact AWS keys, JWTs, and private keys from agent I/O without blocking the request.

```bash
orchestrate controls create \
  --artifact SecretsDetection \
  --name secrets-redactor \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 10 \
  --config '{
    "enabled": {
      "aws_access_key_id": true,
      "aws_secret_access_key": true,
      "jwt_like": true,
      "private_key_block": true,
      "google_api_key": true
    },
    "redact": true,
    "redaction_text": "***REDACTED***",
    "block_on_detection": false
  }' \
  --agent "MyAgent"
```

---

## Recipe 5 — Secrets detection (block mode)

Block the entire request if any credential is detected. Require 2+ findings before blocking.

```bash
orchestrate controls create \
  --artifact SecretsDetection \
  --name secrets-blocker \
  --hook agent_pre_invoke \
  --priority 5 \
  --config '{
    "enabled": {
      "aws_access_key_id": true,
      "aws_secret_access_key": true,
      "jwt_like": true,
      "private_key_block": true
    },
    "block_on_detection": true,
    "min_findings_to_block": 2
  }' \
  --agent "MyAgent"
```

---

## Recipe 6 — Output length truncation

Truncate agent responses at 5000 characters to prevent context-window overflow, stopping at word boundaries.

```bash
orchestrate controls create \
  --artifact OutputLengthGuardPlugin \
  --name output-truncate \
  --hook agent_post_invoke \
  --priority 100 \
  --config '{
    "limit_mode": "character",
    "strategy": "truncate",
    "max_chars": 5000,
    "word_boundary": true,
    "ellipsis": "... [response truncated]"
  }' \
  --agent "MyAgent"
```

---

## Recipe 7 — SQL injection guard on a database tool

Block dangerous SQL statements and unscoped DELETE/UPDATE before the tool executes.

```bash
orchestrate controls create \
  --artifact SQLSanitizer \
  --name db-sql-guard \
  --hook tool_pre_invoke \
  --priority 1 \
  --config '{
    "block_on_violation": true,
    "strip_comments": true,
    "block_delete_without_where": true,
    "block_update_without_where": true,
    "blocked_statements": ["\\\\bDROP\\\\b","\\\\bTRUNCATE\\\\b","\\\\bALTER\\\\b","\\\\bGRANT\\\\b","\\\\bREVOKE\\\\b"]
  }' \
  --tool "my-db-tool"
```

---

## Recipe 8 — Rate limiter on an external API tool

Limit calls to 20/min per tool and 500/min per tenant.

```bash
orchestrate controls create \
  --artifact RateLimiterPlugin \
  --name api-rate-limit \
  --hook tool_pre_invoke \
  --priority 1 \
  --config '{"by_tool": 20, "by_tenant": 500}' \
  --tool "external-api-tool"
```

---

## Recipe 9 — Custom regex filter (company-internal codes)

Redact any mention of internal project codes from agent output.

```bash
orchestrate controls create \
  --artifact RegexPattern \
  --name internal-code-guard \
  --hook agent_post_invoke \
  --priority 80 \
  --config '{
    "regex_patterns": [
      "PROJ-[0-9]{4,}",
      "INTERNAL-[A-Z]+",
      "CONF-[A-Z0-9]+"
    ],
    "strategy": "redact",
    "redaction_text": "[INTERNAL]"
  }' \
  --agent "MyAgent"
```

---

## Recipe 10 — Model fallback (GPT-4 → Granite)

Automatically failover from GPT-4o to IBM Granite on 429/500/503 errors.

```bash
orchestrate controls create \
  --artifact fallback \
  --name gpt4-granite-fallback \
  --config '{
    "fallBack": {
      "strategy": {
        "mode": "fallback",
        "on_status_codes": [429, 500, 502, 503, 504]
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
  }' \
  --model "gpt-4o"
```

---

## Recipe 11 — Load balancing across two Granite models (70/30 split)

Distribute LLM calls 70% to Granite 8B, 30% to Granite 3B.

```bash
orchestrate controls create \
  --artifact load_balance \
  --name granite-load-balance \
  --config '{
    "loadBalance": {
      "strategy": { "mode": "loadbalance" },
      "retry": { "attempts": 1, "on_status_codes": [429, 500, 502] },
      "targets": [
        { "provider": "watsonx", "weight": 70, "override_params": { "model": "ibm/granite-3-8b-instruct" } },
        { "provider": "watsonx", "weight": 30, "override_params": { "model": "ibm/granite-3-3b-instruct" } }
      ]
    }
  }' \
  --model "ibm/granite-3-8b-instruct"
```

---

## Recipe 12 — Retry same model 3 times on rate limits

```bash
orchestrate controls create \
  --artifact retry_mode \
  --name granite-retry \
  --config '{
    "Retry": {
      "strategy": { "mode": "single" },
      "retry": { "attempts": 3, "on_status_codes": [429, 500, 502] },
      "targets": [
        { "provider": "watsonx", "override_params": { "model": "ibm/granite-3-8b-instruct" } }
      ]
    }
  }' \
  --model "ibm/granite-3-8b-instruct"
```

---

## Recipe 13 — Multi-layer defence stack on one agent

Apply three controls at different priorities for defence-in-depth.

```bash
# Layer 1: Block jailbreak (priority 1 — runs first)
orchestrate controls create \
  --artifact Guardrails \
  --name agent-jailbreak-block \
  --hook agent_pre_invoke \
  --priority 1 \
  --config '{"enabled":{"jailbreak":true,"harm":true},"block_message":"Request blocked."}' \
  --agent "test_DA"

# Layer 2: Redact secrets from I/O (priority 10)
orchestrate controls create \
  --artifact SecretsDetection \
  --name agent-secrets-redact \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 10 \
  --config '{"enabled":{"aws_access_key_id":true,"jwt_like":true},"redact":true,"block_on_detection":false}' \
  --agent "test_DA"

# Layer 3: Redact PII from I/O (priority 50)
orchestrate controls create \
  --artifact pii_filter \
  --name agent-pii-redact \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 50 \
  --config '{"detect_ssn":true,"detect_email":true,"detect_phone":true,"default_mask_strategy":"redact","log_detections":true}' \
  --agent "test_DA"

# Verify the stack
orchestrate controls list --agent test_DA
orchestrate controls count
```

---

## Recipe 14 — Update a control to add a new hook

```bash
# Current: agent_pre_invoke only
# Goal: add agent_post_invoke (must re-specify pre_invoke too)
orchestrate controls update \
  --name my-pii-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke
```

---

## Recipe 15 — Rebind a control to a different agent

```bash
orchestrate controls update \
  --name test-da-pii-full \
  --agent "AskOrchestrate"
```

> `--agent` replaces all bindings. Specify multiple `--agent` flags to bind to multiple agents.

---

## Recipe 16 — Export, edit, re-import a control

```bash
# Export current control
orchestrate controls export -n test-da-pii-full -o ./controls/test-da-pii-full.yaml

# Edit the YAML (e.g. change agent binding or config)
# ...

# Re-import (will create or update)
orchestrate controls import -f ./controls/test-da-pii-full.yaml
```
