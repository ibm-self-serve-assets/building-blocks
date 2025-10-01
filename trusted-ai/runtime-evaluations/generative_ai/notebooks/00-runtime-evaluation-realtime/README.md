# Realtime Prompt Evaluation for Production

This repository contains the Jupyter notebook **`Manual_Prompt_Evaluation_for_Production.ipynb`** — a hands‑on, end‑to‑end workbook that: creates a prompt template asset, publishes it to a space, deploys/evaluates prompt subscriptions and collects manual evaluation data via IBM Watson/Watson OpenScale runtime APIs.

The notebook is targeted at IBM Cloud / Cloud Pak for Data (CPD) environments and demonstrates how to: create prompt template assets, publish them to a space, create a subscription (PTA → space), run scoring (generation), capture evaluation/feedback records in OpenScale datasets, and surface monitoring/metrics (Generative AI Quality, Drift V2, Model Risk, Model Health).

---

## Quick summary
The notebook is structured as a tutorial / production playbook for evaluating prompts. It does the following at a high level:
1. Configure credentials & runtime (IBM Cloud vs CPD)
2. (Optionally) create or use an existing project/space
3. Create a *Prompt Template Asset* using the WatsonX prompts API
4. Publish/promote the prompt template to a space (PTA → space)
5. Create a subscription (production subscription) for the prompt template
6. Score test examples (reads CSV input) and store evaluation records in Watson OpenScale datasets
7. Create monitors (Generative AI Quality, Drift V2, Model Risk, Model Health) and read/display metrics
8. Plot simple ROUGE metrics and output details / factsheets URL

---

## Requirements & environment
- **Python**: 3.10+ (notebook top cell states Runtime 22.2 & Python 3.10 or greater)
- **Jupyter Notebook** (or JupyterLab)

Python packages used in the notebook (imports discovered in the notebook):
- `ibm_watsonx_ai`
- `ibm_watson_openscale`
- `ibm_watson_studio_lib`
- `ibm_cloud_sdk_core`
- `matplotlib`
- `requests`
- Standard library: `json`, `csv`, `time`, `uuid`, `copy`

Suggested install (adjust package names/versions as appropriate for your environment):
```bash
python -m venv .venv
source .venv/bin/activate
pip install jupyter matplotlib requests ibm-watsonx-ai ibm-watson-openscale ibm-watson-studio-lib ibm-cloud-sdk-core
```

---

## Where to edit configuration (exact variables + default values)
Below is a focused list of configurable variables found in the notebook with the cell number where they appear and the default/placeholder value you will find in the shipped notebook. Edit these cells before running the notebook.


| Variable | Default / placeholder | Cell # | Purpose / notes |
|---|---:|---:|---|
| `use_cpd` | `False` | 12 | Set to `True` if you are running against an on‑prem Cloud Pak for Data (CPD) instance, `False` for IBM Cloud services. |
| `IAM_URL` | `"https://iam.cloud.ibm.com"` | 12 | IAM endpoint. Change if using CPD or a different region. |
| `DATAPLATFORM_URL` | `"https://api.dataplatform.cloud.ibm.com"` | 12 | Dataplatform base URL (IBM Cloud). |
| `SERVICE_URL` | `"https://aiopenscale.cloud.ibm.com"` | 12 | Watson OpenScale service URL. |
| `CLOUD_API_KEY` | `"<apikey>"` | 12 | Your IBM Cloud API key (placeholder). **Do not commit this** to git. |
| `WML_CREDENTIALS` | a credentials dict (`url` + `apikey`) | 12 | WML / ML runtime credentials dictionary. Fill in `url` and `apikey` appropriately. |
| `project_id` | `"<project_id>"` | 16 | The ID of the project that will host prompt template assets. |
| `use_existing_space` | `True` | 19 | If `True`, notebook uses `existing_space_id`; otherwise creates a new space. |
| `existing_space_id` | `"<space_id>"` | 24 | If using an existing space, place the space id here. |
| `space_name` | `"runtime_evaluation_deployment_space_2"` | 26 | If creating a new space, this will be the display name. |
| `WML_INSTANCE_NAME` | `""` | 28 | Optional: WML instance name (if required by environment). |
| `WML_CRN` | `""` | 28 | Optional: WML instance CRN (Cloud Pak cases). |
| `COS_RESOURCE_CRN` | `' '` | 30 | Cloud Object Storage resource CRN used when creating a new space. |
| `space_id` | `existing_space_id` (by default) | 32 | Notebook variable chosen from `existing_space_id` or newly created space. |
| `test_data_path` | `"summarisation.csv"` | 125 | Input CSV used for running prompts and generating predictions. Supply your own CSV with matching fields. |
| `csv_file_path` | `"summarisation.csv"` | 125 | Alias used for reading CSV in the test data ingestion cell. |
| `prompt_template` (params) | name=`"Summarise input"`, model_id=`"mistralai/mistral-large"`, task_ids=`["summarization"]` | 39 | Prompt template definition; edit `model_id` or `input_text` here to target a different model or task. |
| `verify` | `True` | 97 | If `False` disables SSL verification for `requests` calls (useful for self‑signed certs in CPD). |
| `version` | `'2023-07-07'` | 100 | Model/runtime API version passed to deployment URL assembly. |
| `DEPLOYMENTS_URL` | built from the WML credentials URL | 100 | WML deployments base path (computed). |
| `deployment_id` | `''` (populated later) | 100 | ID of the runtime deployment created/used. |
| `scoring_url` | (computed from subscription/deployment) | 110 | Final scoring/generation endpoint used to send prompt input to the model. |
| `project_pta_id` | (populated after storing prompt template in project) | 39 | ID of the stored Prompt Template Asset (project level). |
| `space_pta_id` | (populated after promoting PTA to space) | 97 | ID of the prompt asset published to the space. |
| `prod_subscription_id` | (populated after creating a production subscription) | 107 | Subscription id for the PTA subscription in the space. |
| `feedback_data_set_id` | `None` (created programmatically) | 123 | Watson OpenScale dataset id used for storing evaluation / feedback records. |
| `fb_records_count` | (populated after storing records) | 128 | Number of records in the feedback dataset (after upload). |
| `mhm_monitor_id` | (Model Health monitor id) | 82 | Populated when creating Model Health monitor. |
| `drift_monitor_id` | (populated when creating Drift V2 monitor) | 157 | Populated when creating Drift v2 monitor instance. |

> Cell numbers above correspond to the notebook's cell index (0‑based). Edit the cell shown to change the variable.

---
## Execution flow
```
flowchart TD

    A[Start Notebook] --> B[Configure Credentials]
    B --> C[Set Project ID]
    C --> D[Select or Create Space]
    D --> E[Generate Access Token]
    E --> F[Create Prompt Template Asset]
    F --> G[Publish Prompt Template to Space]
    G --> H[Create Subscription & Runtime Deployment]
    H --> I[Prepare Test Data & Run Scoring]
    I --> J[Create & Read Monitors / Metrics]
    J --> K[Review & Iterate]
    K --> L[End / Repeat]
```
## Execution order
The notebook contains many cells and interactions with cloud services. The safest way to run is: run cells top‑to‑bottom but pause and verify at key steps.

1. **Start**: open the notebook and read the top markdown cells (cells `0`–`10`) for context.
2. **Configure credentials** (Cell **12**) — edit `CLOUD_API_KEY`, `IAM_URL`, `DATAPLATFORM_URL`, `SERVICE_URL`, and `use_cpd`. If using CPD, set `use_cpd = True` and populate CPD credentials accordingly.
3. **Set project id** (Cell **16**) — set `project_id` to the project that will host prompt template assets.
4. **Space selection** (Cells **19**, **24**, **26**) — decide whether to use an existing space (`use_existing_space = True`) and set `existing_space_id`, or set `use_existing_space = False` to create a new space and edit `space_name`, `COS_RESOURCE_CRN` etc.
5. **Run token / auth helper** (Cell **35**) — run the function that generates an access token (used in later `requests` calls). This cell defines `iam_access_token` in CPD flows.
6. **Create the Prompt Template asset** (Cell **39**) — edit the `PromptTemplate(...)` body to change `model_id`, `input_text` or `task_ids` and run this cell to store the template in the project. This produces `project_pta_id`.
7. **Prompt setup / Publish to space** (Cells around **97**) — promote the PTA to the target space (`space_pta_id` will be populated). If creating new space, ensure `space_id` was created in earlier cells.
8. **Create subscription + runtime deployment** (Cells ~100–110) — creates production subscription and extracts `scoring_url` and `prod_subscription_id`. Depending on environment, the notebook builds `scoring_url` from the subscription details or builds CPD URL for WML.
9. **Prepare test data and run scoring** (Cells **112**–**128**) — reads `test_data_path` / `csv_file_path`, prepares features & predictions, posts to scoring endpoint, and writes records into Watson OpenScale feedback dataset (via `wos_client.data_sets.store_records`). After upload, `fb_records_count` is printed.
10. **Create & read monitors / metrics** (cells **129** onward) — create monitors (MRM, Generative AI Quality, Drift V2) and read metrics. The notebook includes plotting (ROUGEL/ROUGELSUM) and prints a factsheets URL at the end.

> The notebook sometimes pauses with `time.sleep()` to let background processes finish; allow those waits to complete before reading subsequent monitor ids.

---

## Expected outputs
- `project_pta_id` — ID of prompt template asset stored at project level
- `space_pta_id` — ID of prompt template asset promoted to the space
- `prod_subscription_id` — production subscription id for the prompt subscription
- `scoring_url` — final scoring endpoint used for generation requests
- `feedback_data_set_id` — Watson OpenScale dataset id where evaluation/feedback is stored
- `fb_records_count` — number of records stored in the feedback dataset
- Monitor instance ids for Model Health (`mhm_monitor_id`), Drift V2 (`drift_monitor_id`) and Generative AI Quality monitors
- Simple ROUGE plots displayed inline (cells ~90)
- `factsheets_url` — a URL printed at the end that links to factsheets / runtime details in the Cloud UI

Note: Many outputs are stored and viewable in the Watson OpenScale / Watson Studio UI — the notebook primarily triggers those artefacts and reads them back.

---

## Troubleshooting
- **Authentication failures**: double‑check `CLOUD_API_KEY`, `IAM_URL` and whether `use_cpd` is set correctly for your environment.
- **Space creation errors**: ensure that `COS_RESOURCE_CRN` is valid and the IAM principal has permission to create resources and attach COS.
- **SSL / certificate errors in CPD**: set `verify = False` (cell 97) only for local testing; do not use in production.
- **Empty feedback dataset**: confirm `test_data_path` points to a CSV with the expected field names (see `feature_fields` cell). The notebook expects `original_text` as an input field by default.

---

## Where to look in the notebook (short index)
- **Cell 12**: primary environment & credential configuration (CLOUD_API_KEY, DATAPLATFORM_URL, use_cpd)
- **Cell 16**: `project_id`
- **Cell 24–32**: space selection & creation (`existing_space_id`, `space_name`, `COS_RESOURCE_CRN`)
- **Cell 35**: access token generation helper (CPD auth path)
- **Cell 39**: prompt template definition & `prompt_mgr.store_prompt(...)`
- **Cell ~97**: promote PTA to space (`space_pta_id`) and related requests
- **Cell ~100–110**: subscription creation, `scoring_url`, and `deployment_id`
- **Cell 112–128**: read CSV (`test_data_path`) and store feedback records in OpenScale dataset
- **Cell 129 onward**: monitor instance listing, monitor id reads, metrics display and plotting

---

## Final notes
This notebook is a working walkthrough for manual / trigger based prompt evaluation with watsonx.gov on CP4D/SaaS environment. It wires cloud APIs and OpenScale artifacts together as an example flow — before using in production, transform the procedural cells into modular, well‑tested scripts and replace inline secrets with secure secret management.
