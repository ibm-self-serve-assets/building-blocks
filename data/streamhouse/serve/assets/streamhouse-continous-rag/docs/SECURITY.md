# Security and production-hardening notes

## Credentials

Never put Confluent, Schema Registry, model-provider, or watsonx credentials in source control. `.env` is gitignored.

On IBM Cloud Code Engine, use a generic secret and map the secret to environment variables. The deployment script follows this pattern.

## Confluent credentials

Use resource-scoped Kafka keys/service accounts and ACL/RBAC permissions appropriate to the topics the application requires. Separate application credentials from administrator/cloud-management credentials.

The application needs Kafka data-plane access. It does **not** require a Confluent Cloud management API key for its normal runtime path.

## Network/authentication

The demo app does not contain end-user login or authorization. Before exposing it outside a controlled demonstration environment, add an identity-aware access layer and define roles for:
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
