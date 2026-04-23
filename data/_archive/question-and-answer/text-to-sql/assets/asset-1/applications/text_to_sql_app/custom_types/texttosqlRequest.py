from pydantic import BaseModel, Field
from typing import Optional, List

class texttosqlRequest(BaseModel):
    question: str = Field(title="NL Question", description="Question asked by the user.")
    model_id: str = Field(default="meta-llama/llama-3-3-70b-instruct", title="Model Id", description="Model Id")
    container_id: str = Field(title="Project or Container Id", description="Project or Container Id")
    container_type: str = Field(default="project", title="Project or Container", description="Project or Container")
    dialect: str = Field(default="presto", title="Database type", description="Database Type")
    raw_output: str = Field(default="false", title="show raw output form watsonx", description="show raw output form watsonx")
    top_n: str = Field(default="5", title="top n value", description="top n value")
    db_execute: str = Field(default="false", title="Execute the generated SQL", description="Execute the generated SQL")
    