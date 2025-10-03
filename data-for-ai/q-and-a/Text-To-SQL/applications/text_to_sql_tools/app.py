import json
import os
import uvicorn
import sys
import time
import jaydebeapi
import pymysql
import pandas as pd


from pymongo import MongoClient
from dotenv import load_dotenv

# Fast API
from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.middleware.cors import CORSMiddleware


# Custom type classes
from customTypes.text2sqlRequest import text2sqlRequest
from customTypes.text2sqlResponse import text2sqlResponse
from customTypes.queryRequest import queryRequest
from customTypes.querylResponse import queryResponse


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
API_KEY_NAME = "APP-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Token to IBM Cloud
ibm_cloud_api_key = os.environ.get("IBM_CLOUD_API_KEY")
project_id = os.environ.get("WX_PROJECT_ID")
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


print("token")
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
        print(f'updating token')
        token =  get_auth_token(api_key)
        token_updated_at = datetime.now()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

# Caching database connection
db_connections = {}
async def get_db_connection(dbtype):
    if dbtype in db_connections:
        return db_connections[dbtype]

    if dbtype == "DB2":
        SQL_DATABASE_URL = "jdbc:db2://" + str(db2_creds["db_hostname"]) + ":" + str(db2_creds["db_port"]) + "/" + str(db2_creds["db_database"]) + ":currentSchema=" + str(db2_creds["db_schema"]) + ";user=" + str(db2_creds["db_user"]) + ";password=" + str(db2_creds["db_password"]) + ";sslConnection=true;"
        print("SQL created " + SQL_DATABASE_URL)
        conn = jaydebeapi.connect("com.ibm.db2.jcc.DB2Driver", SQL_DATABASE_URL, None, "db2jcc4.jar")
    
    elif dbtype == "MYSQL":

        conn = pymysql.connect(
                        host=str(mysql_creds["db_hostname"]),
                        port=int(mysql_creds["db_port"]),
                        database=str(mysql_creds["db_database"]),
                        user=str(mysql_creds["db_user"]),
                        passwd=str(mysql_creds["db_password"]),
                        ssl={'ca': None})
    
    elif dbtype == "MONGODB":
        tls_ca_file =  str(mdb_creds["tls_location"])
        username = str(mdb_creds["db_user"])
        password = str(mdb_creds["db_password"]) 
        host = str(mdb_creds["db_hostname"])
        port = str(mdb_creds["db_port"])  # default MongoDB port
        conn =  MongoClient(f'mongodb://{username}:{password}@{host}:{port}',tls=True,tlsCAFile=tls_ca_file)
    elif dbtype == "PRESTO":
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

@app.post("/texttosql")
async def texttosql(request: texttosqlRequest, api_key: str = Security(get_api_key)):
    question=request.question
    container_id=equest.container_id
    container_type=request.container_type
    dialect=request.dialect
    top_n=request.top_n
    
    update_token_if_needed(ibm_cloud_api_key)
    params = {'container_id': container_id, 'container_type': container_type, 'dialect': dialect, 'top_n': top_n}

    response = requests.post(text_to_sql_endpoint, headers=headers, json=payload, params=params, verify=False).json()

    print("RESPONSE : " + str(response))
    message = response['generated_sql_queries']['sql']
    print(" message: " + str(message))
    return message

    #v1/text_to_sql?model_id=meta-llama/llama-3-3-70b-instruct&container_id=61f9e0af-0c6a-4127-9b67-5e789f318fff&container_type=project&dialect=presto&top_n=5
    return texttosqlResponse(response=nlResponse)



@app.post("/query")
async def query(request: queryRequest, api_key: str = Security(get_api_key)):
    query = request.query
    conn = await get_db_connection(dbtype)  
    print ("SQL DB Connection: " + str(conn))
  
    cur = conn.cursor()
    
    cur.execute(query)
    rows = cur.fetchall()
    op=""

    for row in rows:
        br="" 
        for i,col in enumerate(row):
            key=cur.description[i][0]
            br += "{}:{},".format(key,col)
        br = br[:-1]
        op += "{" + br + "}"

    nl=""
    history=""
    image=""
    response = dict(answer=op,query=query,nl=nl,history=history,image=image)
    print("Response from queryexec: "+ str(response))
    return queryResponse(response=response)