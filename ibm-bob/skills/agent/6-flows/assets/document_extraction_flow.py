"""
document_extraction_flow.py — Document processing with docproc, docext, docclassifier.

Demonstrates:
- aflow.docproc() for text extraction with KVP schemas
- aflow.docext() for named field extraction with DocExtConfigField + DocExtConfigTableField
- aflow.docclassifier() for document classification
- DocProcOutputFormat.object for inline JSON output
- PageRange to limit extraction to specific pages
- LanguageCode for OCR language specification
- available_options to constrain extracted values
- Explicit map_input() / map_output() when using DocProcOutputFormat.object

Prerequisite: orchestrate server start -e .env -d  (requires 20GB RAM in Docker)
Required .env: WATSONX_SPACE_ID, WATSONX_APIKEY, WATSONX_PROJECT_ID
"""

from typing import Optional
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.types import (
    DocExtConfigField,
    DocExtConfigTableField,
    DocClassifierClass,
    DocumentProcessingCommonInput,
    DocProcInput,
    DocProcOutputFormat,
    PageRange,
    LanguageCode,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Text Extraction — docproc() with KVP schema
# ══════════════════════════════════════════════════════════════════════════════

@flow(
    name="invoice_text_extraction",
    display_name="Invoice Text + KVP Extraction",
    description="Extract raw text and structured key-value pairs from an invoice document.",
    input_schema=DocProcInput
)
def build_invoice_text_extraction(aflow: Flow = None) -> Flow:
    doc_proc_node = aflow.docproc(
        name="extract_invoice_text",
        display_name="Extract Invoice Text",
        task="text_extraction",
        output_format=DocProcOutputFormat.object,    # inline JSON instead of URL
        kvp_schemas=[{
            "document_type": "Invoice",
            "document_description": "Standard seller-to-buyer invoice",
            "fields": {
                "invoice_number": {"description": "Unique invoice identifier", "example": "INV-2025-001", "default": ""},
                "total_amount":   {"description": "Total amount due",          "example": "1500.00",       "default": ""},
                "due_date":       {"description": "Payment due date (ISO)",     "example": "2025-07-01",    "default": ""},
                "vendor_name":    {"description": "Issuing company name",       "example": "Acme Corp",     "default": ""},
                # Table field: line items with columns
                "line_items": {
                    "type": "array",
                    "description": "Invoice line items",
                    "columns": {
                        "item":        {"description": "Item description", "example": "Widget A", "default": ""},
                        "quantity":    {"description": "Quantity ordered",  "example": "10",       "default": ""},
                        "unit_price":  {"description": "Price per unit",    "example": "15.00",    "default": ""},
                        "amount":      {"description": "Line total",        "example": "150.00",   "default": ""},
                    }
                }
            }
        }],
        page_range=PageRange(start=1, end=3)         # extract only first 3 pages
    )

    # Explicit mapping required with DocProcOutputFormat.object
    doc_proc_node.map_input(input_variable="document_ref",         expression="flow.input.document_ref")
    doc_proc_node.map_input(input_variable="kvp_schemas",          expression="flow.input.kvp_schemas")
    doc_proc_node.map_input(input_variable="kvp_model_name",       expression="flow.input.kvp_model_name")
    doc_proc_node.map_input(input_variable="kvp_force_schema_name",expression="flow.input.kvp_force_schema_name")

    aflow.sequence(START, doc_proc_node, END)

    # Explicit output mapping (required for object format)
    aflow.map_output(output_variable="text",  expression='flow["Extract Invoice Text"].output.text')
    aflow.map_output(output_variable="kvps",  expression='flow["Extract Invoice Text"].output.kvps')

    return aflow


# ══════════════════════════════════════════════════════════════════════════════
# 2. Field Extraction — docext() with table fields and available_options
# ══════════════════════════════════════════════════════════════════════════════

class ContractFields(BaseModel):
    """Fields to extract from a contract document."""
    buyer: DocExtConfigField = Field(
        default=DocExtConfigField(name="Buyer", field_name="buyer")
    )
    seller: DocExtConfigField = Field(
        default=DocExtConfigField(name="Seller", field_name="seller")
    )
    agreement_date: DocExtConfigField = Field(
        default=DocExtConfigField(name="Agreement Date", field_name="agreement_date", type="date")
    )
    contract_type: DocExtConfigField = Field(
        default=DocExtConfigField(
            name="Contract Type",
            field_name="contract_type",
            type="string",
            description="Classification of the contract.",
            available_options=["NDA", "MSA", "SOW", "PO", "SLA"]  # constrain to known values
        )
    )
    currency: DocExtConfigField = Field(
        default=DocExtConfigField(
            name="Currency",
            field_name="currency",
            type="string",
            description="Currency symbol (€, $, £) — map to ISO code.",
            available_options=["USD", "EUR", "GBP", "JPY", "CAD"]
        )
    )
    line_items: DocExtConfigTableField = Field(
        default=DocExtConfigTableField(
            name="Line Items",
            field_name="line_items",
            description="Contract line items / deliverables",
            fields=[
                DocExtConfigField(name="Description", field_name="description", type="string"),
                DocExtConfigField(name="Amount",      field_name="amount",      type="number"),
            ]
        )
    )


@flow(
    name="contract_field_extraction",
    display_name="Contract Field Extraction",
    description="Extract structured fields from a contract using AI-driven field extractor.",
    input_schema=DocumentProcessingCommonInput
)
def build_contract_field_extraction(aflow: Flow = None) -> Flow:
    doc_ext_node, ExtractedValues = aflow.docext(
        name="extract_contract_fields",
        display_name="Extract Contract Fields",
        description="Extracts buyer, seller, date, type, currency, and line items from a contract.",
        fields=ContractFields(),
        llm="watsonx/mistralai/mistral-small-3-1-24b-instruct-2503",
        field_extraction_method="layout",    # required for table fields and available_options
        enable_review=True,                  # human-in-the-loop if confidence is low
        min_confidence=0.7
    )
    aflow.sequence(START, doc_ext_node, END)
    return aflow


# ══════════════════════════════════════════════════════════════════════════════
# 3. Field Extraction with OCR Language — docext() for Japanese documents
# ══════════════════════════════════════════════════════════════════════════════

@flow(
    name="japanese_contract_extraction",
    display_name="Japanese Contract Field Extraction",
    description="Extract fields from a Japanese-language scanned contract.",
    input_schema=DocumentProcessingCommonInput
)
def build_japanese_extraction(aflow: Flow = None) -> Flow:
    class SimpleFields(BaseModel):
        buyer:  DocExtConfigField = Field(default=DocExtConfigField(name="Buyer",  field_name="buyer"))
        seller: DocExtConfigField = Field(default=DocExtConfigField(name="Seller", field_name="seller"))

    doc_ext_node, _ = aflow.docext(
        name="japanese_extractor",
        fields=SimpleFields(),
        llm="watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        language=LanguageCode.ja,            # Japanese OCR engine
        field_extraction_method="layout"
    )
    aflow.sequence(START, doc_ext_node, END)
    return aflow


# ══════════════════════════════════════════════════════════════════════════════
# 4. Document Classification — docclassifier()
# ══════════════════════════════════════════════════════════════════════════════

class DocumentClasses(BaseModel):
    invoice:        DocClassifierClass = Field(default=DocClassifierClass(class_name="Invoice"))
    contract:       DocClassifierClass = Field(default=DocClassifierClass(class_name="Contract"))
    tax_form:       DocClassifierClass = Field(default=DocClassifierClass(class_name="TaxForm"))
    bill_of_lading: DocClassifierClass = Field(default=DocClassifierClass(class_name="BillOfLading"))
    receipt:        DocClassifierClass = Field(default=DocClassifierClass(class_name="Receipt"))


@flow(
    name="document_classifier",
    display_name="Document Classifier",
    description="Classify uploaded documents into business categories.",
    input_schema=DocumentProcessingCommonInput
)
def build_document_classifier(aflow: Flow = None) -> Flow:
    classifier_node = aflow.docclassifier(
        name="classify_doc",
        display_name="Classify Document",
        classes=DocumentClasses(),
        llm="watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        min_confidence=0.75,
        enable_review=True    # prompt user to confirm if confidence below threshold
    )
    aflow.sequence(START, classifier_node, END)
    return aflow
