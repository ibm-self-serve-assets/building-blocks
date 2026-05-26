import json
import os
import uvicorn
import sys
import time
import requests
import jaydebeapi
import pymysql
import pandas as pd
import prestodb
import logging
from datetime import datetime, timedelta

from pymongo import MongoClient
from dotenv import load_dotenv

# Fast API
from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.middleware.cors import CORSMiddleware


# Custom type classes
from customTypes.texttosqlRequest import texttosqlRequest
from customTypes.texttosqlResponse import texttosqlResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Set up CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
# RAG APP Security
API_KEY_NAME = "APP-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Token to IBM Cloud
ibm_cloud_api_key = os.environ.get("IBM_CLOUD_API_KEY")
project_id = os.environ.get("WXD_PROJECT_ID")
text_to_sql_endpoint = os.environ.get("TEXT_TO_SQL_ENDPOINT")

# DB2 Creds
db2_creds = {
    "db_hostname": os.environ.get("DB2_HOSTNAME"),
    "db_port": os.environ.get("DB2_PORT"),
    "db_user": os.environ.get("DB2_USERNAME"),
    "db_password": os.environ.get("DB2_PASSWORD"),
    "db_database": os.environ.get("DB2_DATABASE"),
    "db_schema": os.environ.get("DB2_SCHEMA")
}

mysql_creds = {
    "db_hostname": os.environ.get("MYSQL_HOSTNAME"),
    "db_port": os.environ.get("MYSQL_PORT"),
    "db_user": os.environ.get("MYSQL_USERNAME"),
    "db_password": os.environ.get("MYSQL_PASSWORD"),
    "db_database": os.environ.get("MYSQL_DATABASE"),
    "tls_location": os.environ.get("MYSQL_TLS_LOCATION")
}

mdb_creds = {
    "db_hostname": os.environ.get("MDB_HOSTNAME"),
    "db_port": os.environ.get("MDB_PORT"),
    "db_user": os.environ.get("MDB_USERNAME"),
    "db_password": os.environ.get("MDB_PASSWORD"),
    "db_database": os.environ.get("MDB_DATABASE"),
    "db_schema": os.environ.get("MDB_SCHEMA"),
    "tls_location": os.environ.get("MDB_TLS_LOCATION")
}

presto_creds = {
    "db_hostname": os.environ.get("PRESTO_HOSTNAME"),
    "db_port": os.environ.get("PRESTO_PORT"),
    "db_user": os.environ.get("PRESTO_USERNAME"),
    "db_password": os.environ.get("PRESTO_PASSWORD"),
    "db_catalog": os.environ.get("PRESTO_CATALOG"),
    "db_schema": os.environ.get("PRESTO_SCHEMA"),
    "tls_location": os.environ.get("PRESTO_TLS_LOCATION")
}


token_updated_at = None
token = None
headers = None

def get_auth_token(api_key):
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    response = requests.post(auth_url, headers=headers, data=data, verify=False)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get authentication token")

def update_token_if_needed(api_key):
    global token, token_updated_at, headers
    if token is None or datetime.now() - token_updated_at > timedelta(minutes=20):
        token =  get_auth_token(api_key)
        token_updated_at = datetime.now()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

# Basic security for accessing the App
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.environ.get("APP_API_KEY"):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate APP credentials. Please check your ENV."
        )

@app.get("/")
def index():
    return {"IBM": "Build Engineering"}

# Caching database connection
db_connections = {}
async def get_db_connection(dbtype):
    if dbtype in db_connections:
        return db_connections[dbtype]

    if dbtype == "db2":
        SQL_DATABASE_URL = "jdbc:db2://" + str(db2_creds["db_hostname"]) + ":" + str(db2_creds["db_port"]) + "/" + str(db2_creds["db_database"]) + ":currentSchema=" + str(db2_creds["db_schema"]) + ";user=" + str(db2_creds["db_user"]) + ";password=" + str(db2_creds["db_password"]) + ";sslConnection=true;"
        print("SQL created " + SQL_DATABASE_URL)
        conn = jaydebeapi.connect("com.ibm.db2.jcc.DB2Driver", SQL_DATABASE_URL, None, "db2jcc4.jar")
    
    elif dbtype == "mysql":

        conn = pymysql.connect(
                        host=str(mysql_creds["db_hostname"]),
                        port=int(mysql_creds["db_port"]),
                        database=str(mysql_creds["db_database"]),
                        user=str(mysql_creds["db_user"]),
                        passwd=str(mysql_creds["db_password"]),
                        ssl={'ca': None})
    
    elif dbtype == "mongodb":
        tls_ca_file =  str(mdb_creds["tls_location"])
        username = str(mdb_creds["db_user"])
        password = str(mdb_creds["db_password"]) 
        host = str(mdb_creds["db_hostname"])
        port = str(mdb_creds["db_port"])  # default MongoDB port
        conn =  MongoClient(f'mongodb://{username}:{password}@{host}:{port}',tls=True,tlsCAFile=tls_ca_file)
    elif dbtype == "presto":
        #print("in presto" + str(presto_creds["db_password"]) + " " + str(presto_creds["db_user"]) + " " + str(presto_creds["db_hostname"]))
        with prestodb.dbapi.connect(
            host=str(presto_creds["db_hostname"]),
            port=str(presto_creds["db_port"]),
            user=str(presto_creds["db_user"]),
            catalog=str(presto_creds["db_catalog"]),
            schema=str(presto_creds["db_schema"]),
            http_scheme='https',
            auth=prestodb.auth.BasicAuthentication(str(presto_creds["db_user"]), str(presto_creds["db_password"]))
            )as conn:
             #conn._http_session.verify = str(presto_creds["tls_location"])
             conn._http_session.verify = False
    else:
        raise ValueError("Unsupported database type")

    db_connections[dbtype] = conn
    return conn

async def query_exec(query, dbtype):
    conn = await get_db_connection(dbtype)
        
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    # Get column names from cursor description
    columns = [description[0] for description in cur.description]
    
    # Convert rows to a list of dictionaries
    results = []
    for row in rows:
        results.append(dict(zip(columns, row)))
    return results

@app.post("/texttosql")
async def texttosql(request: texttosqlRequest, api_key: str = Security(get_api_key)):
    question=request.question
    container_id=request.container_id
    container_type=request.container_type
    dialect=request.dialect
    top_n=request.top_n
    raw_output=request.raw_output
    db_execute=request.db_execute
    
    update_token_if_needed(ibm_cloud_api_key)

    payload= {
        "query": question,
        "raw_output": raw_output
    }
    
    params = {'container_id': container_id, 'container_type': container_type, 'dialect': dialect, 'top_n': top_n}
    
    response = requests.post(text_to_sql_endpoint, headers=headers, json=payload, params=params, verify=False).json()

    nlResponse = {}

    try:
        query = response['generated_sql_queries'][0]['sql']
        score = response['generated_sql_queries'][0]['score']
        nlResponse['nl_question'] = question
        nlResponse['sql_query'] = query
        nlResponse['score'] = score
        nlResponse['model_id'] = response['model_id']
        nlResponse['token_count'] = response['resource_usage']['token_count']
        nlResponse['cuh'] = response['resource_usage']['cuh']
        if raw_output=="true":
            nlResponse['raw_output'] = response['wx_ai_raw_output']
        if db_execute=="true":
           queryresponse = await query_exec(query.replace(';', ''), dialect)
           nlResponse['query_response'] = queryresponse
        logger.info("Query tranaction complete")
    except IndexError as e:
        logger.error(f"SQL Generate Error: {str(e)}")
        nlResponse['sql_generate_error'] = str(e)
  
  
    return texttosqlResponse(response=nlResponse)


if __name__ == '__main__':
    if 'uvicorn' not in sys.argv[0]:
        uvicorn.run("app:app", host='0.0.0.0', port=4050, reload=True)