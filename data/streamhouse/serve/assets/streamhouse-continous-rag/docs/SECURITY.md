# Security and production-hardening notes

## Credentials

Never put Confluent, Schema Registry, model-provider, or watsonx credentials in source control. `.env` is gitignored.

On IBM Cloud Code Engine, use a generic secret and map the secret to environment variables. The deployment script follows this pattern.

## Confluent credentials

Use resource-scoped Kafka keys/service accounts and ACL/RBAC permissions appropriate to the topics the application requires. Separate application credentials from administrator/cloud-management credentials.

The application needs Kafka data-plane access. It does **not** require a Confluent Cloud management API key for its normal runtime path.

## Network/authentication & API Protection

- **API Key Guard:** All mutating endpoints (`POST /api/knowledge`, `POST /api/rag/ask`, `POST /api/demo/seed-knowledge`, `POST /api/demo/step/*`) are protected by an optional API key (`DEMO_API_KEY`). When set, clients must supply the matching key in the `X-API-Key` header.
- **Rate Limiting:** Ingestion and generation endpoints are protected via `slowapi` rate limiters (e.g. 10 req/min for RAG inference, 30 req/min for knowledge ingestion) to prevent cost DoS and resource starvation.
- **HTTP Security Headers:** Default security headers are enforced across all responses (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy`).
- **Input Validation:** Strict Pydantic models validate input length, allowed source types, and character sets for Kafka keys (`document_id`, `asset_id`) preventing prompt injection and data poisoning.
- **Client-Side Escaping:** The frontend explicitly sanitizes all interpolated data before rendering to the DOM via HTML entity escaping.

Before exposing the application beyond a controlled demonstration environment, add an identity-aware access layer (e.g., App ID, OIDC, or reverse proxy auth) and define fine-grained roles for:
- read-only operators,
- knowledge publishers,
- demo administrators.

## RAG grounding

Every RAG response includes retrieved evidence. The watsonx prompt explicitly instructs generation to use only provided evidence and say when evidence is insufficient.

This reduces but does not eliminate model error. In production:
- add retrieval quality thresholds,
- add source authorization filtering,
- add audit records for question/evidence/answer,
- evaluate faithfulness and answer quality,
- do not allow an LLM response alone to execute safety-critical machine actions.

## Manufacturing safety

All included operating values and work-order content are synthetic. Do not interpret them as machine safety limits. Site procedures, OEM documentation, and qualified personnel must govern real maintenance actions.
