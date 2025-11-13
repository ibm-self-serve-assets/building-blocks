import os
import yaml
import requests
import pandas as pd
import numpy as np
import streamlit as st
from ibm_watson_machine_learning.foundation_models import ModelInference
from ibm_aigov_facts_client import AIGovFactsClient, DetachedPromptTemplate, PromptTemplate
import altair as alt

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, CloudPakForDataAuthenticator
from ibm_watson_openscale import *
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import *

import time
from ibm_watson_openscale.supporting_classes.enums import *

import uuid
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord


# Prompt CSV files
PROMPT_FILES = {
    "RAG": "rag_prompt.csv",
    "Summarization": "summarization_prompt.csv",
}

LLM_PARAMS = ["model", "temperature", "max_tokens", "top_p"]

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    openscale_config = config["openscale"]
    watsonx_config = config["watsonx"]
    dataplatform_url = watsonx_config["dataplatform_url"]



def configure_openscale_metrics(space_pta_id, space_id, deployment_id):
    authenticator = IAMAuthenticator(
         apikey=watsonx_config["api_key"],
         url="https://iam.cloud.ibm.com"
      )
    wos_client = APIClient(
          authenticator=authenticator,
          service_url=openscale_config["url"],
          service_instance_id=openscale_config["service_instance_id"])

    data_mart_id = wos_client.service_instance_id
    print("openscale client version : " , wos_client.version)

    gen_ai_evaluator = wos_client.integrated_systems.add(
            name="llm as a judge",
            description="llm as judge evaluator",
            type="generative_ai_evaluator",
            parameters={
                "evaluator_type": "watsonx.ai",
                "model_id": "meta-llama/llama-3-3-70b-instruct"
            },
            credentials={"url" : watsonx_config["url"], 
               "apikey": watsonx_config["api_key"], 
               "auth_url": "https://iam.cloud.ibm.com",  
               "wml_location" : "cloud"}
        )

    # Get evaluator integrated system ID
    result = gen_ai_evaluator.result._to_dict()
    evaluator_id = result["metadata"]["id"]
    print(f"Evaluator created with ID: {evaluator_id}")
    
    label_column = "answer"
    context_fields = ["context"]
    question_field = "question"
    operational_space_id = "production"
    problem_type= "retrieval_augmented_generation"
    input_data_type= "unstructured_text"

    monitors ={"generative_ai_quality": {
            "parameters": {
                "generative_ai_evaluator": {
                    "enabled": True,
                    "evaluator_id": evaluator_id,
                },
                "min_sample_size": 1,
                "metrics_configuration": {
                    "faithfulness":{},
                    "unsuccessful_requests":{},
                    "answer_relevance": {},
                    "retrieval_quality": {
                        "context_relevance": {}
                    },
                    "answer_similarity": {}
                }
              }
           }
        }
   


    response = wos_client.wos.execute_prompt_setup(prompt_template_asset_id = space_pta_id, 
                                                                   space_id = space_id,
                                                                   deployment_id = deployment_id,
                                                                   label_column = label_column,
                                                                   context_fields=context_fields,     
                                                                   question_field = question_field,   
                                                                   operational_space_id = operational_space_id, 
                                                                   problem_type = problem_type,
                                                                   input_data_type = input_data_type, 
                                                                   supporting_monitors = monitors, 
                                                                   background_mode = True)

    #result = response.result
    #result._to_dict()
    time.sleep(90)
    response = wos_client.monitor_instances.mrm.get_prompt_setup(prompt_template_asset_id = space_pta_id,
                                                             deployment_id = deployment_id,
                                                             space_id = space_id)

    result = response.result
    result_json = result._to_dict()
    print(result_json)
    subscription_id = result_json["subscription_id"]
    return wos_client, data_mart_id, subscription_id

def generate_access_token():
    headers={}
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Accept"] = "application/json"
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": watsonx_config["api_key"],
        "response_type": "cloud_iam"
    }
    response = requests.post("https://iam.cloud.ibm.com/identity/token", data=data, headers=headers)
    json_data = response.json()
    iam_access_token = json_data["access_token"]
        
    return iam_access_token

def render_evaluation_dashboard():
    st.subheader("Evaluation Dashboard")

    with st.expander("Historic Evaluation Metrics & Factsheet", expanded=True):
        # --- Fake historic generative AI quality data (fractional 0 to 1 scale) ---
        gen_ai_data = pd.DataFrame({
            "Date": pd.date_range(start="2025-01-01", periods=10, freq='D'),
            "Faithfulness": [0.80, 0.82, 0.78, 0.85, 0.87, 0.83, 0.81, 0.84, 0.86, 0.82],
            "Unsuccessful Requests": [0.05, 0.04, 0.06, 0.03, 0.05, 0.04, 0.05, 0.06, 0.04, 0.05],
            "Answer Relevance": [0.85, 0.87, 0.83, 0.86, 0.88, 0.84, 0.85, 0.87, 0.86, 0.85],
            "Context Relevance": [0.80, 0.81, 0.79, 0.82, 0.83, 0.81, 0.80, 0.82, 0.81, 0.80],
            "Answer Similarity": [0.90, 0.91, 0.89, 0.92, 0.90, 0.91, 0.89, 0.90, 0.91, 0.90]
        })

        gen_melted = gen_ai_data.melt(id_vars="Date", var_name="Metric", value_name="Score")

        gen_line = alt.Chart(gen_melted).mark_line(point=True).encode(
            x='Date:T',
            y=alt.Y('Score:Q', axis=alt.Axis(format='%')),
            color='Metric:N',
            tooltip=['Date:T', 'Metric:N', alt.Tooltip('Score:Q', format='.2%')]
        )
        st.altair_chart(gen_line, use_container_width=True)

        # --- Fake historic drift data (already fractional) ---
        drift_data = pd.DataFrame({
            "Date": pd.date_range(start="2025-01-01", periods=10, freq='D'),
            "Confidence Drift": [0.03, 0.04, 0.02, 0.06, 0.05, 0.03, 0.04, 0.05, 0.02, 0.04],
            "Prediction Drift": [0.04, 0.03, 0.05, 0.06, 0.04, 0.05, 0.03, 0.04, 0.05, 0.03],
            "Input Metadata Drift": [0.02, 0.03, 0.01, 0.04, 0.03, 0.02, 0.03, 0.02, 0.03, 0.01],
            "Output Metadata Drift": [0.03, 0.04, 0.03, 0.05, 0.04, 0.03, 0.04, 0.03, 0.04, 0.03]
        })

        drift_thresholds = {
            "Confidence Drift": 0.05,
            "Prediction Drift": 0.05,
            "Input Metadata Drift": 0.05,
            "Output Metadata Drift": 0.05
        }

        drift_melted = drift_data.melt(id_vars="Date", var_name="Metric", value_name="Drift Score")
        drift_line = alt.Chart(drift_melted).mark_line(point=True).encode(
            x='Date:T',
            y=alt.Y('Drift Score:Q', axis=alt.Axis(format='%')),
            color='Metric:N',
            tooltip=['Date:T', 'Metric:N', alt.Tooltip('Drift Score:Q', format='.2%')]
        )

        threshold_lines = alt.Chart(pd.DataFrame([
            {"Metric": k, "Threshold": v} for k, v in drift_thresholds.items()
        ])).mark_rule(color='red', strokeDash=[4,4]).encode(
            y='Threshold:Q',
            detail='Metric:N'
        )

        st.altair_chart(drift_line + threshold_lines, use_container_width=True)

        # --- Factsheet link ---
        project_pta_id = "400f2f5c-4fa3-480c-9334-67e30471f468"
        project_id = "2ee97ecb-f652-41a9-b360-dd2a7d594a8b"
        factsheet_url = f"https://dataplatform.cloud.ibm.com/wx/prompt-details/{project_pta_id}/factsheet?context=wx&project_id={project_id}"
        st.markdown(f"[View Factsheet]({factsheet_url})", unsafe_allow_html=True)
# --- Utility Functions ---
def _ensure_csv(file_path: str):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["prompt_id", "prompt_name", "system_prompt", "pta_id", "wos_subscription_id"] + LLM_PARAMS)
        df.to_csv(file_path, index=False)

def _load_prompts(mode: str) -> pd.DataFrame:
    _ensure_csv(PROMPT_FILES[mode])
    return pd.read_csv(PROMPT_FILES[mode])

def _save_prompt(mode: str, system_prompt: str, params: dict) -> pd.DataFrame:
    _ensure_csv(PROMPT_FILES[mode])
    df = pd.read_csv(PROMPT_FILES[mode])
    new_id = len(df) + 1
    new_row = {"prompt_id": new_id, "system_prompt": system_prompt}
    new_row.update(params)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PROMPT_FILES[mode], index=False)
    return df

# --- Watsonx Streaming Call ---
def _call_watsonx_stream(system_prompt, context, question, params):
    prompt_text = f"{system_prompt}\tContext: {context}\tQuestion: {question}"

    # Convert numeric types
    params_serializable = {
        k: (int(v) if isinstance(v, (np.integer,)) 
            else float(v) if isinstance(v, (np.floating,)) 
            else v)
        for k, v in params.items()
    }

    # Setup inference client
    model_inference = ModelInference(
        model_id=params_serializable["model"],
        credentials={"url": watsonx_config["url"], "apikey": watsonx_config["api_key"]},
        project_id=watsonx_config["project_id"],
    )

    # Stream answer
    placeholder = st.empty()
    params_serializable = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,}
    print(prompt_text, params_serializable)
    generated_text = model_inference.generate_text (prompt = prompt_text, params = params_serializable)
    print(generated_text)
    #for chunk in model_inference.generate_text_stream(prompt=prompt_text, params=params_serializable):
    #    generated_text += chunk
    st.markdown (generated_text)
    return generated_text

def _save_prompt_with_watsonx(mode: str, prompt_name: str, system_prompt: str, params: dict) -> pd.DataFrame:
    """
    Saves a system prompt to CSV and publishes it as a detached prompt in Watsonx.ai.

    Args:
        mode (str): "RAG" or "Summarization"
        system_prompt (str): The system prompt text from Streamlit input
        params (dict): Dictionary of LLM parameters (model, temperature, top_p, max_tokens)

    Returns:
        pd.DataFrame: Updated prompt CSV including pta_id
    """
    csv_file = PROMPT_FILES[mode]
    _ensure_csv(csv_file)
    df = pd.read_csv(csv_file)

    # --- Create detached prompt in Watsonx.ai ---
    facts_client = AIGovFactsClient(
        api_key=watsonx_config["api_key"],
        container_id=watsonx_config["project_id"],
        container_type="project",
        disable_tracing=True
    )

    detached_info = DetachedPromptTemplate(
        prompt_id="detached_prompt",
        model_id=params.get("model", "mistralai/mistral-large"),
        model_provider="watsonx.ai",
        model_name=params.get("model", "mistralai/mistral-large"),
        model_url=watsonx_config["url"],
        prompt_url="prompt_url",
        prompt_additional_info={"IBM Cloud Region": "us-south"}
    )
     
    prompt = system_prompt + "{context}{question}"
    prompt_variables = {"context": "", "question": ""}
    prompt_template = PromptTemplate(
        input=system_prompt,
        prompt_variables=prompt_variables,
        input_prefix="",
        output_prefix=""
    )

    pta_details = facts_client.assets.create_detached_prompt(
        model_id=params.get("model"),
        task_id="retrieval_augmented_generation",
        name=prompt_name,
        description=f"{mode} system prompt created for RAG via Streamlit",
        prompt_details=prompt_template,
        detached_information=detached_info
    )

    pta_id = pta_details.to_dict()["asset_id"]

    print(" Prompt Template ID : ", pta_id)

    space_id = watsonx_config ["space_id"]
    
    space_pta_id = promote_prompt_to_space(pta_id)
    
    print(" Space Prompt Template ID : ", space_pta_id)

    deployment_id = create_prompt_deployment(space_pta_id , space_id)
 
    print(" Deployment ID : ", deployment_id)
    
    wos_client, datamart_id, subscription_id = configure_openscale_metrics(space_pta_id, space_id, deployment_id)


    # --- Save to CSV ---
    new_id = len(df) + 1
    new_row = {"prompt_id": new_id, "system_prompt": system_prompt, "pta_id": pta_id, "wos_subscription_id": subscription_id}

    new_row.update(params)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_file, index=False)

    return df

def promote_prompt_to_space(project_pta_id :str):
    headers={}
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    iam_access_token = generate_access_token()
    headers["Authorization"] = "Bearer {}".format(iam_access_token)
    verify = False

    url = "{}/v2/assets/{}/promote".format(dataplatform_url , project_pta_id)

    params = {
     "project_id": watsonx_config["project_id"]
    }

    payload = {
     "space_id": watsonx_config["space_id"]
    }
    response = requests.post(url, json=payload, headers=headers, params = params, verify = verify)
    json_data = response.json()
    space_pta_id = json_data["metadata"]["asset_id"]
    return space_pta_id


def create_prompt_deployment(space_pta_id : str, space_id: str):
    
    headers={}
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    iam_access_token = generate_access_token()
    headers["Authorization"] = "Bearer {}".format(iam_access_token)
    verify = False
    
    deployment_url = watsonx_config["url"] + "/ml/v4/deployments"
    payload = {
    	"prompt_template": {
      		"id": space_pta_id
    	},
    	"detached": {
    	},
    	"base_model_id": "meta-llama/llama-3-70b-instruct",
    	"description": "rag qa deployment",
    	"name": "RAG Prompt Evaluation",
    	"space_id": space_id
	}

    version = "2023-07-07" # The version date for the API of the form YYYY-MM-DD. Example : 2023-07-07
    params = {
            "version":version,
            "space_id":space_id
         }

    response = requests.post(deployment_url, json=payload, headers=headers, params = params, verify = verify)
    json_data = response.json()


    if "metadata" in json_data:
         deployment_id = json_data["metadata"]["id"]
         print(deployment_id)
    else:
         print(json_data)

    return deployment_id


def payload_logging_openscale(payload: str, subscription_id: str):

    authenticator = IAMAuthenticator(
         apikey=watsonx_config["api_key"],
         url="https://iam.cloud.ibm.com"
      )
    wos_client = APIClient(
          authenticator=authenticator,
          service_url=openscale_config["url"],
          service_instance_id=openscale_config["service_instance_id"])

    data_mart_id = wos_client.service_instance_id
    print(wos_client.version)

    time.sleep(5)
    payload_data_set_id = None 
    payload_data_set_id = wos_client.data_sets.list(type=DataSetTypes.PAYLOAD_LOGGING, 
                                                target_target_id=subscription_id, 
                                                target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id
    if payload_data_set_id is None:
    	print("Payload data set not found. Please check subscription status.")
    else:
        print("Payload data set id: ", payload_data_set_id)

    wos_client.data_sets.store_records(data_set_id=payload_data_set_id, request_body=payload , background_mode=False)
    time.sleep(5)
    pl_records_count = wos_client.data_sets.get_records_count(payload_data_set_id) 
    print(pl_records_count)


# --- Streamlit UI ---
def _render_header():
    st.set_page_config(page_title="🛡️ IBM Trusted AI Runtime Evaluation", layout="wide")
    st.title("🛡️ IBM Trusted AI: Runtime Evaluation")
    st.markdown("**Powered by IBM watsonx.governance**  |  Evaluate text content in production")
    st.write("---")

def _llm_prompt_configuration(mode: str, tab_name: str):
    with st.expander("Configure LLM Prompt", expanded=True):
        prompt_name = st.text_input("Prompt Name", key=f"{tab_name}_prompt_name")
        system_prompt = st.text_area("Enter system prompt", key=f"{tab_name}_system_prompt")
        params = {}
        params["model"] = st.text_input("Model", value="mistralai/mistral-large", key=f"{tab_name}_model")
        params["temperature"] = st.slider("temperature", 0.0, 1.0, 0.7, key=f"{tab_name}_temperature")
        params["top_p"] = st.slider("top_p", 0.0, 1.0, 0.9, key=f"{tab_name}_top_p")
        params["max_tokens"] = st.number_input("max_tokens", min_value=1, max_value=2048, value=256, step=1, key=f"{tab_name}_max_tokens")
        df = None
        if st.button(f"Save {tab_name} Prompt", key=f"save_{tab_name}_prompt"):
           if system_prompt.strip():
              df = _save_prompt_with_watsonx(mode, prompt_name, system_prompt, params)
              st.success(f"{tab_name} system prompt saved and published to Watsonx.ai!")
              st.dataframe(df)
           else:
              st.warning("System prompt cannot be empty.")
        return df

def _prompt_selection(mode: str, tab_name: str, df : pd.DataFrame):
    with st.expander("Select prompt for evaluation", expanded=True):
        prompts_df = _load_prompts(mode)
        generated_text = " "
         	
        if not prompts_df.empty:
            selected_idx = st.radio(
                f"Select a {tab_name} prompt to attach to evaluation",
                prompts_df.index,
                format_func=lambda idx: f"[{prompts_df.loc[idx, 'prompt_id']}] {prompts_df.loc[idx, 'system_prompt']} (Model: {prompts_df.loc[idx, 'model']})",
                key=f"select_{tab_name}_prompt"
            )
            st.write(f"Selected prompt: {prompts_df.loc[selected_idx, 'system_prompt']}")

            context = st.text_area("Context", key=f"{tab_name}_context")
            question = st.text_input("Question", key=f"{tab_name}_question")

            if st.button("Ask", key=f"{tab_name}_ask"):
                params = {param: prompts_df.loc[selected_idx, param] for param in LLM_PARAMS}
                print("1")
                generated_text = _call_watsonx_stream(prompts_df.loc[selected_idx, 'system_prompt'], context, question, params)
                print("2")
				
                payload = [{
    		 "request": {
        		"parameters": {
            			"template_variables": {"context" : context, "question": question}
        		}
    		  },
                  "response": {
                  "results": [
                    {"generated_text": generated_text}
                  ]
                 } 
                }]
                payload_logging_openscale(payload,  prompts_df["wos_subscription_id"])

        else:
            st.info(f"No {tab_name} prompts available. Please create one above.")
        return generated_text


def main():
    st.set_page_config(page_title="🛡️ IBM Trusted AI Runtime Evaluation", layout="wide")
    st.title("🛡️ IBM Trusted AI: Runtime Evaluation")
    st.markdown("**Powered by IBM watsonx.governance**  |  Evaluate text content in production")
    st.write("---")

    with st.sidebar:
        st.header("Evaluation Metrics Configuration")
        with st.expander("RAG", expanded=False):
            min_samples = st.number_input("Minimum Samples", value=10, step=1)

            st.subheader("Generative AI Quality Metrics")
            faithfulness = st.slider("Faithfulness Threshold", 0.0, 1.0, 0.8, step=0.01)
            unsuccessful_requests = st.slider("Unsuccessful Requests Threshold", 0.0, 1.0, 1.0, step=0.01)
            answer_relevance = st.slider("Answer Relevance Threshold", 0.0, 1.0, 0.85, step=0.01)
            context_relevance = st.slider("Context Relevance Threshold", 0.0, 1.0, 0.8, step=0.01)
            answer_similarity = st.slider("Answer Similarity Threshold", 0.0, 1.0, 0.9, step=0.01)

            st.session_state["generative_ai_quality"] = {
                "enabled": True,
                "metrics_configuration": {
                    "faithfulness": {"threshold": faithfulness},
                    "unsuccessful_requests": {"threshold": unsuccessful_requests},
                    "answer_relevance": {"threshold": answer_relevance},
                    "retrieval_quality": {"context_relevance": {"threshold": context_relevance}},
                    "answer_similarity": {"threshold": answer_similarity}
                }
            }

            st.subheader("Drift Monitoring (drift_v2)")
            confidence_drift = st.slider("Confidence Drift Threshold", 0.0, 1.0, 0.05, step=0.01)
            prediction_drift = st.slider("Prediction Drift Threshold", 0.0, 1.0, 0.05, step=0.01)
            input_metadata_drift = st.slider("Input Metadata Drift Threshold", 0.0, 1.0, 0.05, step=0.01)
            output_metadata_drift = st.slider("Output Metadata Drift Threshold", 0.0, 1.0, 0.05, step=0.01)

            st.session_state["drift_v2"] = {
                "thresholds": [
                    {"metric_id": "confidence_drift_score", "type": "upper_limit", "value": confidence_drift},
                    {"metric_id": "prediction_drift_score", "type": "upper_limit", "value": prediction_drift},
                    {
                        "metric_id": "input_metadata_drift_score",
                        "type": "upper_limit",
                        "specific_values": [
                            {
                                "applies_to": [{"type": "tag", "key": "field_type", "value": "subscription"}],
                                "value": input_metadata_drift
                            }
                        ]
                    },
                    {
                        "metric_id": "output_metadata_drift_score",
                        "type": "upper_limit",
                        "specific_values": [
                            {
                                "applies_to": [{"type": "tag", "key": "field_type", "value": "subscription"}],
                                "value": output_metadata_drift
                            }
                        ]
                    }
                ],
                "parameters": {"min_samples": min_samples}
            }

        with st.expander("Summarization", expanded=False):
            st.checkbox("Enable Summarization", value=True, key="sidebar_summarization_enable")
            st.slider("Summary Ratio", 0.1, 0.9, 0.3, key="sidebar_summarization_ratio")

    tab_rag, tab_summarization = st.tabs(["RAG", "Summarization"])

    with tab_rag:
        df = _llm_prompt_configuration("RAG", "RAG")
        _prompt_selection("RAG", "RAG", df)
        render_evaluation_dashboard()

    with tab_summarization:
        df = _llm_prompt_configuration("Summarization", "Summarization")
        _prompt_selection("Summarization", "Summarization", df)

if __name__ == "__main__":
    main()

