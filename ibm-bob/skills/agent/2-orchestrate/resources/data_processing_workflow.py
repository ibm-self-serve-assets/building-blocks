#!/usr/bin/env python3
"""
Data Processing Pipeline Workflow
Sequential workflow with validation and transformation
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END


class DataInput(BaseModel):
    """Input schema for data processing"""
    source: str = Field(description="Data source identifier")


class DataOutput(BaseModel):
    """Output schema for data processing"""
    report: str = Field(description="Generated analysis report")


@flow(
    name="data_processing_pipeline",
    display_name="Data Processing Pipeline",
    description="Fetch, validate, transform, analyze, and report on data",
    input_schema=DataInput,
    output_schema=DataOutput
)
def build_data_pipeline(aflow: Flow) -> Flow:
    """
    Complete data processing pipeline with validation
    
    Flow: Start → Fetch → Validate → Branch → [Transform → Analyze → Report] → End
    """
    
    # Define nodes
    fetch_data = aflow.tool("fetch_data_source")
    validate = aflow.agent(
        name="validate",
        agent="data_validator",
        message="Validate the fetched data for quality and completeness"
    )
    
    # Add validation branch
    validation_branch = aflow.branch(
        evaluator="flow.state.validation_passed == true"
    )
    
    transform = aflow.tool("transform_data")
    analyze = aflow.agent(
        name="analyze",
        agent="data_analyzer",
        message="Perform statistical analysis on the transformed data"
    )
    generate_report = aflow.tool("generate_report")
    
    # Connect nodes
    aflow.edge(START, fetch_data)
    aflow.edge(fetch_data, validate)
    aflow.edge(validate, validation_branch)
    
    # Validation branch paths
    validation_branch.case(True, transform)   # Validation passed
    validation_branch.case(False, END)        # Validation failed
    
    aflow.edge(transform, analyze)
    aflow.edge(analyze, generate_report)
    aflow.edge(generate_report, END)
    
    return aflow


if __name__ == "__main__":
    print("Data processing pipeline workflow defined")
    print("Import with: orchestrate tools import -k flow -f data_processing_workflow.py")

# Made with Bob
