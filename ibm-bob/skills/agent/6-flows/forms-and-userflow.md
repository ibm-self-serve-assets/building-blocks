# Forms and User Activity Nodes

User activity nodes let agents collect input from or display output to users in chat — either as a multi-turn conversation (one field at a time) or as a form (multiple fields in a single turn).

---

## Multi-Turn Conversation — `userflow.field()`

Collect or display one value at a time using `field()` on a `userflow()` object.

```python
user_flow = aflow.userflow()
user_flow.spec.display_name = "Collect Info"

name_input = user_flow.field(
    direction="input",           # "input" = collect from user, "output" = display to user
    name="user_name",
    display_name="Your Name",
    kind=UserFieldKind.Text,
    text="Please enter your name"
)

greeting_output = user_flow.field(
    direction="output",
    name="greeting",
    display_name="Welcome",
    kind=UserFieldKind.Text,
    text="Hello, {flow.userflow_1.user_name.output.value}!"
)

user_flow.edge(START, name_input)
user_flow.edge(name_input, greeting_output)
user_flow.edge(greeting_output, END)
aflow.sequence(START, user_flow, END)
```

### `field()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Internal identifier |
| `kind` | ✅ | `UserFieldKind` enum value |
| `direction` | ✅ | `"input"` or `"output"` |
| `display_name` | | Label shown to user |
| `text` | | Display text. Supports `{flow.variable}` expressions |
| `default` | | Default value |
| `option` | | List of predefined options |
| `is_list` | | Accept multiple values |
| `min` / `max` | | Range constraints |
| `input_map` | | `DataMap` for explicit mapping |

### `UserFieldKind` Values

`Text`, `Date`, `DateTime`, `Time`, `Number`, `File`, `Boolean`, `Object`, `Choice`, `List`

---

## Forms — `userflow.form()`

Prompt users for multiple pieces of data in a single conversational turn.

```python
user_flow = aflow.userflow()
user_flow.spec.display_name = "Application"

form = user_flow.form(
    name="app_form",
    display_name="Application Form",
    instructions="Please complete all required fields.",
    submit_button_label="Submit",
    cancel_button_label="Cancel"    # set None to hide cancel button
)

# Add fields to the form (see field types below)
form.text_input_field(name="last_name", label="Last Name", required=True)
form.number_input_field(name="age", label="Age", required=True)

user_flow.edge(START, form)
user_flow.edge(form, END)
aflow.sequence(START, user_flow, END)
```

---

## Form Field Types

### `text_input_field`
Single-line or multi-line text input.

```python
form.text_input_field(
    name="comments",
    label="Comments",
    required=True,
    single_line=False,              # True = single line, False = textarea
    placeholder_text="Enter comments here",
    help_text="Max 500 characters",
    regex="^[a-zA-Z0-9\\s]+$",
    regex_error_message="No special characters allowed"
)
```

### `number_input_field`
Integer or decimal number.

```python
form.number_input_field(
    name="salary",
    label="Desired Salary",
    is_integer=False,               # True = integer only
    help_text="Annual salary in USD"
)
```

### `boolean_input_field`
Checkbox or radio buttons.

```python
form.boolean_input_field(
    name="married",
    label="Marital Status",
    single_checkbox=True,           # False = radio buttons
    true_label="Married",
    false_label="Single"
)
```

### `single_choice_input_field`
Dropdown or radio button selection.

```python
choices_map = DataMap()
choices_map.add(Assignment(target_variable="self.input.choices", value_expression="flow.input.salutations"))

form.single_choice_input_field(
    name="salutation",
    label="Salutation",
    required=True,
    choices=choices_map,
    show_as_dropdown=True,          # False = radio buttons
    placeholder_text="Select title"
)
```

### `multi_choice_input_field`
Multi-select dropdown or checkboxes.

```python
form.multi_choice_input_field(
    name="languages",
    label="Known Languages",
    choices=choices_map,
    show_as_dropdown=True,          # False = checkboxes
    minItems=1,
    maxItems=5
)
```

### `date_input_field`
Date picker.

```python
form.date_input_field(
    name="start_date",
    label="Start Date",
    required=True,
    multiple_dates=False
)
```

### `date_range_input_field`
Start and end date pickers.

```python
form.date_range_input_field(
    name="vacation",
    label="Vacation Dates",
    start_date_label="From",
    end_date_label="To"
)
```

### `datetime_input_field` / `datetime_range_input_field`
DateTime or Time input.

```python
form.datetime_input_field(
    name="meeting_time",
    label="Meeting Time",
    inputType=UserFieldKind.DateTime  # or UserFieldKind.Time
)
```

### `file_upload_field`
File upload with type and size restrictions.

```python
form.file_upload_field(
    name="resume",
    label="Upload Resume",
    required=True,
    allow_multiple_files=False,
    file_max_size=10,               # MB
    supported_file_types=["pdf", "docx"]
)
```

### `file_download_field`
Present a file for download.

```python
download_map = DataMap()
download_map.add(Assignment(target_variable="self.input.value", value_expression="flow.nodes['generate_report'].output.file_url"))
form.file_download_field(name="report", label="Download Report", value=download_map)
```

### `message_output_field`
Display static text.

```python
form.message_output_field(name="success", label="Status", message="Application submitted successfully.")
```

### `field_output_field`
Display a dynamic value.

```python
value_map = DataMap()
value_map.add(Assignment(target_variable="self.input.value", value_expression="flow.input.salary_expectation"))
form.field_output_field(name="projected_salary", label="Projected Salary", value=value_map)
```

### `list_output_field`
Display tabular data (read-only).

```python
data_map = DataMap()
data_map.add(Assignment(target_variable="self.input.choices", value_expression="flow.input.friends.listOfNames"))
form.list_output_field(
    name="friends",
    label="Friends",
    choices=data_map,
    columns={"first_name": "First", "last_name": "Last"}  # field → column label
)
```

### `list_input_field`
Editable table.

```python
form.list_input_field(
    name="books",
    label="Books",
    default=books_map,
    isRowAddable=True,
    isRowDeletable=True,
    columns={"title": "Title", "author": "Author"}
)
```

### `user_input_field`
User/people picker.

```python
form.user_input_field(
    name="approvers",
    label="Select Approvers",
    required=True,
    multiple_users=True,
    min_num_users=min_map,          # DataMap
    max_num_users=max_map           # DataMap
)
```

---

## Multiple Form Buttons

```python
save_btn   = user_flow.add_button("Save Draft")
review_btn = user_flow.add_button("Submit for Review")

submit_node = user_flow.script(name="process_submit", script='print("Submitting...")')
draft_node  = user_flow.script(name="process_draft",  script='print("Saving draft...")')

user_flow.edge(START, form)
user_flow.edge(form,       submit_node, button_label="Submit")   # default Submit button
user_flow.edge(save_btn,   draft_node)
user_flow.edge(draft_node, END)
user_flow.edge(submit_node, END)
```

---

## Dynamic Forms

Control field visibility, labels, and choices based on user interactions.

### `visibility_behaviour_field`
Show/hide fields when another field's value changes.

```python
from ibm_watsonx_orchestrate.flow_builder.utils import RuleBuilder

form.visibility_behaviour_field(
    name="country_visibility",
    on_change_to_field="country",
    rules=[
        RuleBuilder.visibility_rule(
            field_name="country", field_value="USA",
            impacted_field="state", visible_when_true=True, operator="equals"
        )
    ]
)
```

### `label_behaviour_field`
Change a field's label when another field's value changes.

```python
form.label_behaviour_field(
    name="region_label",
    on_change_to_field="country",
    rules=[
        RuleBuilder.label_rule(
            field_name="country", field_value="USA",
            impacted_field="region",
            label_when_true="State", label_when_false="Province",
            operator="equals"
        )
    ]
)
```

### `value_source_behaviour_field`
Populate a field's choices dynamically from a tool.

```python
form.value_source_behaviour_field(
    name="region_choices",
    on_change_to_field="country",
    impacted_field="region",
    tool_name="get_states_or_provinces",
    tool_id="9f0ecb53-dbd9-4e41-be46-29c8d47d6df8",
    field_mappings={"country": "parent.field.country"}
)
```

---

## Multi-User Assignment

Assign a user flow to a specific user instead of the flow initiator.

```python
from ibm_watsonx_orchestrate.flow_builder.types import UserAssignmentPolicy

# Assign to a specific user (resolved at runtime via expression)
user_flow.assign_to(
    policy=UserAssignmentPolicy.USER,
    assignees="flow.private.designated_approver"
)

# Assign to flow initiator (default)
user_flow.assign_to(policy=UserAssignmentPolicy.FLOW_INITIATOR)
```

To look up a user at runtime, use a script node:

```python
init = aflow.script(
    name="find_approver",
    script="flow.private.designated_approver = system.user.search_by_email('approver@example.com')[0]"
)
```

See [`assets/approval_flow.py`](./assets/approval_flow.py) for a complete multi-user assignment example.

---

## Multi-Language Support

Configure translations for all user-facing text in user activity nodes.

```python
# In your @flow function body:
aflow.target_locales(["fr", "es", "de", "ja"])   # languages to support
aflow.source_locale("en")                         # default source language
aflow.translation_enabled(True)                   # enable (default)
```

**What gets translated:** field labels, display names, help text, placeholder text, form instructions, button labels, choice option labels, error messages.

**What does NOT get translated:** user input, dynamic content from variables, tool outputs, flow expressions, variable names, tool/flow names.

### Translation Workflow

```bash
# 1. Import the flow
orchestrate tools import -k flow -f my_flow.py

# 2. Export translations to CSV
orchestrate tools export -k flow my_flow_name --translation translations.csv

# 3. Add translations to the CSV, then import back
orchestrate tools import -k flow -f my_flow.py --translation translations.csv
```

### Supported Locales

`en`, `fr`, `es`, `de`, `it`, `ja`, `ko`, `zh-CN`, `zh-TW`, `pt-BR`

See [`assets/multi_language_flow.py`](./assets/multi_language_flow.py) for a complete multilingual form example.
