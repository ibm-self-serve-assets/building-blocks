from pydantic import BaseModel, Field


class TextToSQLRequest(BaseModel):
    question: str = Field(description="Natural-language question")
    container_id: str = Field(description="IBM watsonx.data intelligence project/container ID")
    container_type: str = Field(default="project")
    dialect: str = Field(default="presto", description="SQL dialect; optional execution is limited to IBM Db2 or watsonx.data Presto")
    raw_output: bool = Field(default=False)
    top_n: int = Field(default=5, ge=1, le=20)
    db_execute: bool = Field(default=False, description="Optional controlled read-only execution; disabled by server configuration by default")
