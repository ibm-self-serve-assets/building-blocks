# Document Processing Nodes

Three document processing nodes are available in ADK flows (all Public Preview). All require the developer edition to be started with the `-d` flag:

```bash
orchestrate server start -e .env -d
```

> **Note:** Requires minimum 20 GB RAM allocated to Docker for document processing features.

---

## Document Text Extractor — `aflow.docproc()`

Extract plain text and key-value pairs (KVPs) from documents.

```python
from ibm_watsonx_orchestrate.flow_builder.types import DocProcInput

@flow(name="text_extraction_flow", input_schema=DocProcInput)
def build_flow(aflow: Flow) -> Flow:
    doc_proc_node = aflow.docproc(
        name="text_extraction",
        display_name="Extract Text",
        description="Extract text from document",
        task="text_extraction",        # only supported value
    )
    aflow.sequence(START, doc_proc_node, END)
    return aflow
```

### `docproc()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Node identifier |
| `task` | ✅ | `"text_extraction"` |
| `display_name` | | Human-readable name |
| `description` | | Node description |
| `output_format` | | `DocProcOutputFormat.docref` (default — URL) or `DocProcOutputFormat.object` (inline JSON) |
| `document_structure` | | Include structural fields (headings, paragraphs). Default: `False` |
| `kvp_schemas` | | Key-value pair extraction schemas (see below) |
| `kvp_model_name` | | LLM for KVP extraction. Default: `watsonx/mistralai/mistral-small-3-1-24b-instruct-2503` |
| `kvp_force_schema_name` | | Force a specific schema for KVP extraction |
| `kvp_enable_text_hints` | | Enable text hints for KVP extraction |
| `page_range` | | `PageRange(start=1, end=5)` — limit extraction to page range |
| `language` | | `LanguageCode` enum for OCR language (e.g., `LanguageCode.ja`) |
| `enable_hw` | | Enable handwritten text recognition |
| `input_map` | | `DataMap` for explicit input mapping |

### Output Format

- **`DocProcOutputFormat.docref`** (default): Returns a URL to the stored extraction result. Best for large documents.
- **`DocProcOutputFormat.object`**: Returns inline JSON. Best for small documents or when output feeds into downstream nodes. When using this format, **always use explicit `map_input()` and `map_output()`** to prevent automap from injecting large structures into LLM context.

### KVP Extraction

Extract structured key-value pairs alongside text:

```python
doc_proc_node = aflow.docproc(
    name="invoice_extraction",
    task="text_extraction",
    kvp_schemas=[{
        "document_type": "Invoice",
        "document_description": "Standard seller-to-buyer invoice",
        "fields": {
            "invoice_number": {"description": "Unique invoice ID", "example": "INV-001", "default": ""},
            "total_amount":   {"description": "Total amount due",  "example": "1500.00", "default": ""},
            "due_date":       {"description": "Payment due date",  "example": "2025-01-01", "default": ""}
        }
    }]
)
```

For **table fields** in KVP schemas, use `"type": "array"` with a `"columns"` definition.

### Page Range

```python
from ibm_watsonx_orchestrate.flow_builder.types import PageRange

doc_proc_node = aflow.docproc(
    name="extract_pages",
    task="text_extraction",
    page_range=PageRange(start=1, end=5)   # extract only pages 1-5
)
```

See [`assets/document_extraction_flow.py`](./assets/document_extraction_flow.py) for complete examples including KVP extraction and `DocProcOutputFormat.object`.

---

## Document Field Extractor — `aflow.docext()`

Extract specific named fields from documents using an LLM.

```python
from ibm_watsonx_orchestrate.flow_builder.types import DocExtConfigField, DocumentProcessingCommonInput
from pydantic import BaseModel, Field

class ContractFields(BaseModel):
    buyer: DocExtConfigField = Field(
        default=DocExtConfigField(name="Buyer", field_name="buyer")
    )
    seller: DocExtConfigField = Field(
        default=DocExtConfigField(name="Seller", field_name="seller")
    )
    agreement_date: DocExtConfigField = Field(
        default=DocExtConfigField(
            name="Agreement Date",
            field_name="agreement_date",
            type="date"
        )
    )

@flow(name="contract_extractor", input_schema=DocumentProcessingCommonInput)
def build_flow(aflow: Flow) -> Flow:
    doc_ext_node, ExtractedValues = aflow.docext(
        name="extract_contract_fields",
        display_name="Extract Contract Fields",
        fields=ContractFields(),
        llm="watsonx/mistralai/mistral-small-3-1-24b-instruct-2503"
    )
    aflow.sequence(START, doc_ext_node, END)
    return aflow
```

> `aflow.docext()` returns **two objects**: the node and the output schema (`_ExtractedValues`). Use `_ExtractedValues` as the `input_schema` for downstream nodes.

### `docext()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Node identifier |
| `fields` | ✅ | Instance of your `BaseModel` containing `DocExtConfigField` definitions |
| `llm` | | LLM for field extraction. Default: `watsonx/meta-llama/llama-3-2-90b-vision-instruct` |
| `display_name` | | Human-readable name |
| `description` | | Node description |
| `field_extraction_method` | | `"classic"` (default, Unstructured extractor) or `"layout"` (Structured extractor) |
| `page_range` | | `PageRange(start, end)` — only valid with `field_extraction_method="layout"` |
| `language` | | `LanguageCode` for OCR (e.g., `LanguageCode.fr`) |
| `enable_hw` | | Enable handwritten recognition |
| `min_confidence` | | Minimum confidence for human-in-the-loop review |
| `review_fields` | | List of field names that require user review |
| `enable_review` | | Enable human-in-the-loop review. Default: `False` |
| `input_map` | | `DataMap` |

### `DocExtConfigField` Fields

| Field | Description |
|---|---|
| `name` | Display name of the field |
| `field_name` | Internal field key |
| `type` | `"string"`, `"date"`, `"number"` |
| `description` | Hints the LLM on what to extract |
| `example_value` | Example to guide extraction |
| `available_options` | Constrain extracted value to a list (requires `field_extraction_method="layout"`) |

### Table Field Extraction

Use `DocExtConfigTableField` to extract multi-row tabular data. Requires `field_extraction_method="layout"`.

```python
from ibm_watsonx_orchestrate.flow_builder.types import DocExtConfigField, DocExtConfigTableField

line_items = DocExtConfigTableField(
    name="Invoice Line Items",
    field_name="line_items",
    description="Line items from the invoice",
    fields=[
        DocExtConfigField(name="Item",     field_name="item",       type="string"),
        DocExtConfigField(name="Quantity", field_name="quantity",   type="number"),
        DocExtConfigField(name="Amount",   field_name="amount",     type="number"),
    ]
)
```

### OCR Language Support

For scanned PDFs and images with non-Latin scripts, specify the language:

```python
from ibm_watsonx_orchestrate.flow_builder.types import LanguageCode

doc_ext_node, _ = aflow.docext(
    name="japanese_contract_extractor",
    fields=ContractFields(),
    language=LanguageCode.ja,
    field_extraction_method="layout"
)
```

See [`assets/document_extraction_flow.py`](./assets/document_extraction_flow.py) for complete field extraction examples.

---

## Document Classifier — `aflow.docclassifier()`

Classify documents into predefined categories using an LLM.

```python
from ibm_watsonx_orchestrate.flow_builder.types import DocClassifierClass, DocumentProcessingCommonInput
from pydantic import BaseModel, Field

class DocumentClasses(BaseModel):
    invoice:        DocClassifierClass = Field(default=DocClassifierClass(class_name="Invoice"))
    contract:       DocClassifierClass = Field(default=DocClassifierClass(class_name="Contract"))
    tax_form:       DocClassifierClass = Field(default=DocClassifierClass(class_name="TaxForm"))
    bill_of_lading: DocClassifierClass = Field(default=DocClassifierClass(class_name="BillOfLading"))

@flow(name="doc_classifier", input_schema=DocumentProcessingCommonInput)
def build_flow(aflow: Flow) -> Flow:
    classifier_node = aflow.docclassifier(
        name="classify_document",
        display_name="Classify Document",
        classes=DocumentClasses(),
        llm="watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    )
    aflow.sequence(START, classifier_node, END)
    return aflow
```

### `docclassifier()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Node identifier |
| `llm` | ✅ | LLM for classification. Default: `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8` |
| `classes` | ✅ | Instance of your `BaseModel` containing `DocClassifierClass` definitions |
| `display_name` | | Human-readable name |
| `description` | | Node description |
| `min_confidence` | | Minimum confidence for human-in-the-loop review trigger |
| `enable_review` | | Enable review. Default: `False` |
| `enable_hw` | | Enable handwritten recognition |
| `language` | | `LanguageCode` for OCR |
| `input_map` | | `DataMap` |

### Output Schema

The output is a `DocumentClassificationResponse` object with the classified class and confidence score.

---

## File Limits

| Area | Limit |
|---|---|
| Max file size | 10 MB (Excel: 0.1 MB) |
| Max files per invocation | 5 |
| Accepted types | `.doc`, `.docx`, `.jpe`, `.jpeg`, `.jpg`, `.pdf`, `.png`, `.ppt`, `.pptx`, `.tif`, `.tiff`, `.xlsx` |
| Max pages (`docext`, `docclassifier`) | 600 |

---

## Required `.env` Credentials

```bash
# For docext and docproc
WATSONX_SPACE_ID=...
WATSONX_APIKEY=...
WATSONX_PROJECT_ID=...

# For docclassifier
WO_INSTANCE=...
WO_API_KEY=...
AUTHORIZATION_URL=...
```
