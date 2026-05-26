# watsonx Orchestrate Knowledge Bases
Guide to creating, importing, and attaching knowledge bases into watsonx Orchestrate where a knowledge base gives agents grounded retrieval over domain content.

A knowledge base gives agents grounded retrieval over domain content. Use knowledge bases for policy, product docs, support content, playbooks, procedures, and other content the agent should retrieve from rather than invent. Do not use a knowledge base for actions. Use tools for actions.

```text
Agent -> knowledge_base -> built-in Milvus index OR external search/vector store
```

## Knowledge base types

| Type | Use when | Key configuration |
|---|---|---|
| Built-in | Orchestrate should ingest local files into built-in Milvus. | `documents`, optional `vector_index` |
| External Milvus | Content is already embedded/indexed in Milvus. | `conversational_search_tool.index_config[].milvus` |
| External Elasticsearch | Content is in Elasticsearch. | `index`, `query_body`, `result_filter`, `field_mapping` |
| External OpenSearch | Content is in OpenSearch, often with hybrid search. | `search_mode`, `vector_field`, `text_field`, `field_mapping` |
| AstraDB | Content is in DataStax AstraDB. | `api_endpoint`, `keyspace`, `data_type`, `collection` or table config |
| Custom search | Retrieval is handled by a custom search service. | `custom_search.url`, optional `filter`, optional `metadata` |

## Authoring rule: minimize YAML examples

This file intentionally keeps only one complete YAML example. When generating new KB guidance, prefer tables, field notes, and small inline field lists instead of additional fenced YAML blocks.

## Canonical built-in knowledge base YAML

Use this as the default pattern when the user has local documents and no existing external vector/search system.

```yaml
spec_version: v1
kind: knowledge_base
name: contract_playbook_kb
description: |
  Contract review playbook, clause guidance, fallback positions, and risk rules.
documents:
  - path: docs/contract_playbook.pdf
    url: https://example.com/contract-playbook
  - path: docs/vendor_terms_guidelines.docx
vector_index:
  embeddings_model_name: ibm/slate-125m-english-rtrvr-v2
  chunk_size: 400
  chunk_overlap: 50
conversational_search_tool:
  query_source: Agent
  generation:
    prompt_instruction: |
      Answer only from retrieved content. If the content is insufficient,
      say that the playbook does not contain enough information.
    max_docs_passed_to_llm: 10
    generated_response_length: Moderate
    idk_message: "I don't have enough information in the knowledge base to answer."
  confidence_thresholds:
    retrieval_confidence_threshold: Low
    response_confidence_threshold: Low
  query_rewrite:
    enabled: true
  citations:
    citations_shown: -1
```

Built-in constraints:

- Each file must have a unique filename.
- Up to 100 files per knowledge base YAML.
- `.xlsx`: max 1 MB.
- `.docx`, `.pdf`, `.pptx`: max 25 MB.
- `.csv`, `.html`, `.txt`: max 5 MB.
- If `embeddings_model_name` is omitted, the default is `ibm/slate-125m-english-rtrvr-v2`.

## Attach a knowledge base to an agent

In the agent spec, reference the KB by exact name:

- `knowledge_base: [contract_playbook_kb]`
- Add instructions that state when the KB is required.
- Tell the agent not to answer from memory when the KB should be authoritative.
- If retrieved content does not answer the question, the agent should say so.

Recommended agent instruction lines:

- Use `contract_playbook_kb` for clause policy, fallback positions, and approval guidance.
- If the KB does not contain the answer, state that the playbook does not specify it.
- Do not invent policy, contract terms, approval thresholds, or legal requirements.

## External knowledge base patterns

For external KBs, keep `kind: knowledge_base` and replace local `documents` with `conversational_search_tool.index_config` for the provider.

### Common external fields

| Field | Purpose |
|---|---|
| `prioritize_built_in_index: false` | Tells Orchestrate to use the external search/vector source rather than built-in documents first. |
| `conversational_search_tool.language` | Search language, for example `en`. |
| `conversational_search_tool.query_source` | Use `Agent` for dynamic mode; use `SessionHistory` for classic mode. |
| `field_mapping.title` | Search result title field. |
| `field_mapping.body` | Search result body/content field. |
| `field_mapping.url` | Optional source URL field. |
| `field_mapping.custom_fields` | Optional provider-specific fields returned to the agent. |

### Milvus external KB fields

Use when content is already embedded and indexed in Milvus.

| Field | Note |
|---|---|
| `grpc_host` / `grpc_port` | Use GRPC host/port, not HTTP host/port. |
| `database` | Milvus database name. |
| `collection` | Collection containing the indexed content. |
| `index` | Milvus index name, if required. |
| `embedding_model_id` | Must match the model used for ingestion. |
| `filter` | Optional provider-side filter expression. |
| `field_mapping` | Required so Orchestrate can identify title/body/url fields. |

### Elasticsearch external KB fields

Use when content is in Elasticsearch.

| Field | Note |
|---|---|
| `url` | Elasticsearch endpoint. |
| `index` | Index name. |
| `port` | Usually `9200` or hosted-provider port. |
| `query_body` | Optional custom query. Must include `$QUERY`. |
| `result_filter` | Optional result filter. If used with `query_body`, the query body must include `$FILTER`. |
| `field_mapping` | Required. Include `title`, `body`, and optional `url`. |

### OpenSearch external KB fields

Use when content is in OpenSearch, especially for hybrid search.

| Field | Note |
|---|---|
| `url`, `index`, `port` | OpenSearch endpoint information. |
| `search_mode` | Common values include lexical, vector, or hybrid depending on provider support. |
| `embedding_mode` | Server-side or client-side embedding mode. |
| `vector_field` | Field containing embeddings. |
| `text_field` | Field containing passage text. |
| `field_mapping` | Map title/body/url fields. |
| `representation: tool` | Use when the external KB is represented as a tool-like retrieval source. |

### AstraDB external KB fields

Use when content is stored in DataStax AstraDB.

| Field | Note |
|---|---|
| `api_endpoint` | AstraDB API endpoint. |
| `keyspace` | AstraDB keyspace. |
| `data_type` | `collection` or `table`. |
| `collection` | Collection name when `data_type` is `collection`. |
| `embedding_model_id` | Must match ingestion embedding model. |
| `embedding_mode` | `server` or `client`. |
| `search_mode` | For collection: vector, lexical, or hybrid; for table: vector. |
| `filter` | Optional JSON filter string. |
| `limit` | Max returned results. |
| `field_mapping` | Map title/body/url fields. |

### Custom search external KB fields

Use when retrieval is handled by a custom search service.

| Field | Note |
|---|---|
| `custom_search.url` | Endpoint Orchestrate calls for retrieval. |
| `custom_search.filter` | Optional static filter such as product or tenant scope. |
| `custom_search.metadata` | Optional metadata passed with the request. |

If the custom search service requires credentials, create a connection and import the KB with `--app-id`.

## Dynamic input for external knowledge bases

Use `input_schema` when the agent should fill structured retrieval parameters at runtime.

Rules:

- Dynamic input schema is available only in Agent mode: `query_source: Agent`.
- Placeholders use `{field_name}` syntax in filters.
- If an input field name matches a context variable, the input value overwrites that context variable.
- `custom_fields` can return extra fields to the agent.

Common dynamic fields:

| Field | Purpose |
|---|---|
| `conversational_search_tool.query_source: Agent` | Lets the agent supply query parameters. |
| `input_schema.type: object` | Defines structured runtime input. |
| `input_schema.properties.<field>` | Defines a runtime filter/input field. |
| `input_schema.properties.<field>.enum` | Restricts allowed values. |
| `result_filter` with `{field_name}` | Injects runtime input into provider-side filtering. |

## Generation and retrieval options

Use these options to control answer style, grounding behavior, citations, and fallback behavior.

| Option | Purpose | Notes |
|---|---|---|
| `generation.prompt_instruction` | KB-specific generation instruction. | Use to force grounded answers. |
| `generation.max_docs_passed_to_llm` | Number of retrieved docs passed to the LLM. | Valid range is 1–20. |
| `generation.generated_response_length` | Answer length. | `Concise`, `Moderate`, or `Verbose`; default is `Moderate`. |
| `generation.idk_message` | Fallback when content is insufficient. | Use for high-risk domains. |
| `confidence_thresholds.retrieval_confidence_threshold` | Minimum retrieval confidence. | `Off`, `Lowest`, `Low`, `High`, `Highest`. |
| `confidence_thresholds.response_confidence_threshold` | Minimum response confidence. | `Off`, `Lowest`, `Low`, `High`, `Highest`. |
| `query_rewrite.enabled` | Enables query rewrite. | Enabled by default. |
| `citations.citations_shown` | Citation count. | `-1` all, `0` none, or positive max count. |

For dynamic knowledge bases, only `max_docs_passed_to_llm` and `citations_shown` apply; other generation settings are ignored.

## Knowledge base modes

| Mode | `query_source` | Behavior |
|---|---|---|
| Dynamic / Agent mode | `Agent` | Agent supplies the query and determines how to use retrieved content. This is usually the preferred mode for agent workflows. |
| Classic mode | `SessionHistory` | Session history/user input is used to generate the query and the KB flow returns a generated response. |

## CLI: import and manage

Import built-in or external KB:

```bash
orchestrate knowledge-bases import -f knowledgebases/contract_playbook_kb.yaml
```

Safe import/update:

```bash
orchestrate knowledge-bases import -f knowledgebases/contract_playbook_kb.yaml --safe
```

Import external KB with credentials:

```bash
orchestrate connections add \
  -a elastic_credentials \
  --component knowledge \
  --category elastic_search

orchestrate connections configure \
  -a elastic_credentials \
  --env draft \
  --kind basic \
  --type team

orchestrate connections set-credentials \
  -a elastic_credentials \
  --env draft \
  -u "$ELASTIC_USER" \
  -p "$ELASTIC_PASSWORD"

orchestrate knowledge-bases import \
  -f knowledgebases/support_elasticsearch_kb.yaml \
  -a elastic_credentials
```

Check ingestion/index status:

```bash
orchestrate knowledge-bases status --name contract_playbook_kb
```

Update by re-importing the same KB name:

```bash
orchestrate knowledge-bases import -f knowledgebases/contract_playbook_kb.yaml
```

List:

```bash
orchestrate knowledge-bases list
```

Export KB spec:

```bash
orchestrate knowledge-bases export \
  -n contract_playbook_kb \
  -o contract_playbook_kb.yaml
```

Remove:

```bash
orchestrate knowledge-bases remove --name contract_playbook_kb
```

## Model authoring checklist

When generating a knowledge base file:

1. Use `kind: knowledge_base`.
2. Use a short `snake_case` `name`.
3. Write a description that tells agents when to use the KB.
4. Choose built-in if the user has files and no existing vector/search system.
5. Choose external if the user already has Milvus, Elasticsearch, OpenSearch, AstraDB, or custom search.
6. Always include `field_mapping` for external KBs.
7. For Elasticsearch with custom `query_body`, include `$QUERY` and include `$FILTER` if `result_filter` is used.
8. Use `query_source: Agent` for dynamic mode.
9. Use `idk_message` and confidence thresholds when hallucination risk matters.
10. Attach the KB to agents by adding its exact name under `knowledge_base`.
11. Verify indexing with `orchestrate knowledge-bases status --name <kb_name>` before relying on it in an agent.
