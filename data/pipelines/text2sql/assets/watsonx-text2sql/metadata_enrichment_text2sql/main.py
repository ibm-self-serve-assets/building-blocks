import os
from fastapi import FastAPI
from pydantic import BaseModel
from config import access_token
from logs.logging_config import setup_logging
from metadata_enrichment import MetaDataEnrichment
from text2sql_generation import Text2SQLGeneration

logger = setup_logging()

app = FastAPI()

# Request body for table import from watsonx.data presto
class PrestoData(BaseModel):
    file_name: str
    path_to_asset: str

# Request body for text2sql generation
class Text2sqlData(BaseModel):
    query: str

@app.get("/")
def read_root():
    """
        Metadata enrichment and Text2SQL generation home page
    """
    return {"message": "Metadata Enrichment and Text2SQL Generator"}


@app.post("/import_data_wxdi/")
def import_data_wxdi(PrestoData: PrestoData):
    """
        Import the data from watsonx.data(presto) to watsonx.data intelligence project and 
        start the metadata enrichment process.
        args: file_name(str), path_to_asset(str)
        return: enrichment_job_id (str)
    """
    try:
        mdeObj = MetaDataEnrichment()
        logger.info("Started importing data from watsonx.data presto to watsonx.data intelligences")
        data_asset_ids = mdeObj.import_data_to_wxdi_project(PrestoData.file_name, PrestoData.path_to_asset)
        logger.info("Metadata enrichment started")
        job_response = mdeObj.execute_metadata_enrichment_job(data_asset_ids, PrestoData.file_name)
        logger.info("Job ID generated for metadata enrichment")
        job_id = job_response.json()['entity']['job']['id']

        return {
                "message": f"Metadata enrichment started for asset id {data_asset_ids}. Use the enrichment_job_id to check the job status",
                "enrichment_job_id": job_id
                }
    except Exception as ex:
        return {
            "Error" : f"Data import from watsonx.data presto failed {ex}"
        }


@app.get("/check_enrichment_status/{job_id}")
def check_enrichment_status(job_id : str):
    """
        It checks the status of metadata enrichment job.
        args: job_id(str) (Metadata enrichment job id)
        return: state (str) (Returns completed or failed status)
    """
    try:
        mdeObj = MetaDataEnrichment()
        logger.info("Check the metadata enrichment job status")
        state = mdeObj.check_job_status(job_id)
        print(state)
        if state == "Completed":
            return {
                "message": "Data imported to watsonx.data intelligence successfully. Performed metadata enrichment successfully",
                "enrichment_status": "Completed"
                }
        else:
            return {
                "message": "Metadata enrichment waas not successful",
                "enrichment_status": state
                }
    except Exception as ex:
        return {
            "Error" : f"Data import from watsonx.data presto failed {ex}"
        }


@app.put("/onboard_text2sql/")
def onboard_text2sql():
    """
        It is to onboard the text2sql capability to the watsonx.data intelligence project.
        return: container_details (JSON) (Returns container id(ie, project id) and container type)
    """
    try:
        text2sqlObj = Text2SQLGeneration()
        response = text2sqlObj.onboard_text2sql_capabilities()
        response = {
            "container_details" : response,
            "message" : "Text2SQL onboarding completed successfully"
        }
        return response
    except Exception as ex:
        return {
            "ERROR" : f"Something went wrong {ex}"
        }


@app.post("/generate_text2sql/")
def generate_text2sql(Text2sqlData: Text2sqlData):
    """
        It checks the status of metadata enrichment job.
        args: query(str) (User's request to create an sql command)
        return: Text2SQL_Generation (JSON) (Returns a json response with generated_sql_queries in it)
    """
    try:
        text2sqlObj = Text2SQLGeneration()
        response = text2sqlObj.generate_text2sql_content(Text2sqlData)
        response = {
            "Text2SQL_Generation" : response,
            "message" : "Text2SQL generation completed successfully"
        }
        return response
    except Exception as ex:
        return {
            "ERROR" : f"Something went wrong {ex}"
        }
