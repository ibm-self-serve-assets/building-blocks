# Data Mapping

Data mapping controls how values flow between nodes. The ADK supports both **automatic mapping** (schema-driven) and **explicit mapping** (`map_input()` / `map_output()` / `DataMap`).

---

## Automatic Mapping

When nodes have matching schemas, the flow engine maps outputs to inputs automatically. If data exceeds token limits, enable compression (see [`getting-started.md`](./getting-started.md#context-window-management)).

---

## Explicit Mapping — `map_input()` / `map_output()`

Call `map_input()` or `map_output()` directly on a node to bind specific fields.

```python
combine_node = aflow.tool(combine_names)
combine_node.map_input(
    input_variable="first_name",
    expression="flow.input.first_name"
)
combine_node.map_input(
    input_variable="last_name",
    expression="flow.input.last_name",
    default_value="Unknown"
)

# Map a flow-level output
aflow.map_output(
    output_variable="summary",
    expression="flow.nodes['summarize_node'].output.text"
)

# Conditional expression
aflow.map_output(
    output_variable="justification",
    expression="flow.Classifier_Node.output.justification_text if flow.Classifier_Node.output.justification_text else 'N/A'"
)
```

### `map_input()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `input_variable` | ✅ | Target input field name |
| `expression` | ✅ | Source expression (flow variable path or Python expression) |
| `default_value` | | Fallback if expression resolves to null |

### `map_output()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `output_variable` | ✅ | Output field name to set |
| `expression` | ✅ | Source expression |
| `default_value` | | Fallback if expression resolves to null |

---

## DataMap + Assignment

For nodes that accept an `input_map` parameter, construct a `DataMap` with `Assignment` objects.

```python
from ibm_watsonx_orchestrate.flow_builder.data_map import DataMap, Assignment

data_map = DataMap()
data_map.add(Assignment(
    target_variable="self.input.choices",
    value_expression="flow.input.salutations"
))
data_map.add(Assignment(
    target_variable="self.input.default",
    value_expression="flow.input.default_salutation"
))

form.single_choice_input_field(
    name="salutation",
    label="Salutation",
    choices=data_map
)
```

Use `has_no_value=True` for an explicit empty/null assignment:

```python
data_map.add(Assignment(
    target_variable="self.input.choices",
    value_expression="",
    has_no_value=True
))
```

---

## Private Schema (`flow.private`)

Use `private_schema` on the `@flow` decorator to define internal flow state that is **not exposed to users or agents**.

```python
from pydantic import BaseModel, Field

class PrivateState(BaseModel):
    user_id: str = Field(default="")
    auth_token: str = Field(default="")
    attempts: int = Field(default=0)

@flow(
    name="my_flow",
    input_schema=MyInput,
    output_schema=MyOutput,
    private_schema=PrivateState       # private state
)
def build_flow(aflow: Flow) -> Flow:
    init = aflow.script(
        name="init",
        script="""
flow.private.user_id = f"USR-{hash(flow.input.username) % 10000}"
flow.private.attempts = 0
"""
    )
    # private fields accessible in all script nodes and expressions
    return aflow
```

**Rules:**
- Private fields are readable/writable from any script node
- Private fields are NOT visible in flow output or user interfaces
- Use for tokens, internal IDs, sensitive intermediate data

---

## Masking Sensitive Data — `aflow.mask_property()`

Mask sensitive fields in logs, UI display, and user flows.

```python
from ibm_watsonx_orchestrate.flow_builder.masking_utils import MaskingPolicy, InputPolicy

# Mask a flow input field
aflow.mask_property("flow.input.ssn", masking_policy=MaskingPolicy.MASK_ALL)

# Mask a private variable
aflow.mask_property("flow.private.auth_token", masking_policy=MaskingPolicy.MASK_FIRST4)

# Mask a script node output
aflow.mask_property(f"flow.{script_node.spec.name}.output.masked_ssn",
                    masking_policy=MaskingPolicy.MASK_FIRST4)

# Mask a form field (with real-time input masking)
aflow.mask_property(f"flow.userflow_1.ApplicationForm.output.password",
                    masking_policy=MaskingPolicy.MASK_ALL,
                    input_policy=InputPolicy.MASK_WHILE_TYPING)

# Mask a tool output
aflow.mask_property(f"flow.{tool_node.spec.name}.output.api_token",
                    masking_policy=MaskingPolicy.MASK_LAST4)
```

### `MaskingPolicy` Values

| Value | Behavior |
|---|---|
| `MASK_ALL` | Replace entire value with mask characters |
| `MASK_FIRST4` | Mask first 4 characters |
| `MASK_LAST4` | Mask last 4 characters |

### `InputPolicy` Values

| Value | Behavior |
|---|---|
| `MASK_WHILE_TYPING` | Mask in real-time as user types in form fields |

### Custom Regex Masking

```python
aflow.mask_property(
    "flow.input.credit_card",
    masking_policy=MaskingPolicy.MASK_ALL,
    regex_config={
        "text-pattern": r"(\d{4})-(\d{4})-(\d{4})-(\d{4})",
        "masking-pattern": "$1-****-****-$4"
    }
)
```

See [`assets/masking_flow.py`](./assets/masking_flow.py) for a comprehensive masking example covering all node types.

---

## Schema Definitions on Nodes

Every node accepts `input_schema` and `output_schema` Pydantic models to enforce type safety.

```python
class ExtractedInfo(BaseModel):
    name: str = Field(description="Customer name")
    email: str = Field(description="Customer email")
    issue: str = Field(description="Support issue summary")

prompt_node = aflow.prompt(
    name="extract_info",
    system_prompt=["Extract structured info from the message."],
    user_prompt=["{message}"],
    input_schema=SupportMessage,
    output_schema=ExtractedInfo
)
# Downstream nodes can reference: flow.extract_info.output.name
```

---

## Expression Reference

Full expression syntax for conditions, loop evaluators, and mapping:

| Expression | Description |
|---|---|
| `flow.input.<field>` | Flow input |
| `flow.output.<field>` | Flow output |
| `flow.private.<field>` | Private state |
| `flow.<node_name>.output.<field>` | Named node output |
| `flow.nodes['<name>'].output.<field>` | Node output (bracket syntax) |
| `flow["<node_name>"]["<field>"].output.value` | User flow field output |
| `parent.input.<field>` | Parent flow input (inside sub-flows) |
| `parent._current_index` | Current foreach index |
| `parent._current_item` | Current foreach item |
| `self.output.<field>` | Current script node output |
| `self["input"]["<field>"]` | Current node's input |
