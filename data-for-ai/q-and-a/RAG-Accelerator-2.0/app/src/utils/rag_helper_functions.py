import requests
import os
import re
import json    
from functools import reduce
from dotenv import load_dotenv
import logging
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output,Markdown
from ibm_watsonx_ai import APIClient
from app.src.utils import config

# -----------------------------------------------------
# Load .env
# -----------------------------------------------------
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("rag_helper_functions")

all_parameters = config.PARAMETERS
parameter_sets_list = list(all_parameters.keys())

def get_parameter_sets(parameter_sets):

    parameters = {}
    for parameter_set in parameter_sets:
        parameters.update(all_parameters[parameter_set])
    print("parameter sets retrieved")
    return parameters


def get_parameters(client,param_set_ids):
    parameters_list = [] 
    for i in param_set_ids.values():
        parameters_list= parameters_list+client.parameter_sets.get_details(i)['entity']['parameter_set']['parameters']
    parameters = {param['name']: param['value'] for param in parameters_list}
    return parameters
    

def update_parameter_set(client,paramset_name,parameter_to_be_updated):
    paramset_id = client.parameter_sets.get_id_by_name(paramset_name)
    parameter_values_list =client.parameter_sets.get_details(paramset_id)['entity']['parameter_set']['parameters']
    parameter_values_updated_list = parameter_values_list
    for parameter in parameter_values_list:
        if parameter['name'] == parameter_to_be_updated['name']:
            parameter['value'] = parameter_to_be_updated['value']

    parameter_set_details = client.parameter_sets.update(paramset_id, parameter_values_updated_list, "parameters")
    return True

parameters=get_parameter_sets(parameter_sets_list)

def promote_assets(client, asset_type, asset_name, parameters, project_asset_id, project_id, space_uid):
    task_type = "list"
    assets_obj = getattr(client,asset_type)
    method = getattr(assets_obj, task_type)  
    asset_df=method()
    if asset_name in asset_df["NAME"].values and parameters['reuse_existing_space_assets']=='True' :
        filtered_df = asset_df[asset_df["NAME"] == asset_name].iloc[0]
        if asset_type=="data_assets":
            space_asset_id = filtered_df["ASSET_ID"]
        else:
            space_asset_id = filtered_df["ID"]
        print(f"Existing asset ID for {asset_name}: {space_asset_id}")
    else:
        # Promote the connection
        space_asset_id=client.spaces.promote(project_asset_id, project_id, space_uid)
        print(f"Promoted the asset {asset_name} to deployment space.")
    return space_asset_id

def create_and_check_elastic_client(es_connection, elastic_search_model_id):
    from elasticsearch import Elasticsearch
    """
    Create an Elasticsearch client and check the status of a trained model.

    Parameters:
    - es_connection (dict): A dictionary containing the connection parameters for Elasticsearch.
    - elastic_search_model_id (str): The model ID for the Elasticsearch trained model.

    Returns:
    - es_client (Elasticsearch client): The Elasticsearch client instance if successful.
    """
    try:
        # Create the Elasticsearch client instance
        print("Reading from the connection..")
        ssl_certificate_content = es_connection.get('ssl_certificate') if es_connection.get('ssl_certificate') else ""
        cert_file_path = "es_conn.crt"
        
        with open(cert_file_path, 'w') as file:
            file.write(ssl_certificate_content)
        
        # Create Elasticsearch client with appropriate authentication method
        if es_connection.get('api_key'):
            print("Connecting to Elastic Search using Elastic Search URL and API key.")
            es_client = Elasticsearch(
                es_connection['url'],
                api_key=es_connection['api_key'],
                headers={'Content-Type': 'application/json'},
                ca_certs=cert_file_path,
                timeout=300, max_retries=10, retry_on_timeout=True
            )
        elif es_connection.get('username'):
            print("Connecting to Elastic Search using Elastic Search username and password.")
            es_client = Elasticsearch(
                es_connection['url'],
                basic_auth=(es_connection['username'], es_connection['password']),
                headers={'Content-Type': 'application/json'},
                ca_certs=cert_file_path,
                timeout=300, max_retries=10, retry_on_timeout=True
            )
        else:
            raise ValueError("Error: No valid Elasticsearch connection parameters provided.")
        
        # Check if the Elasticsearch client is connected successfully
        if es_client.ping():
            print("Successfully connected to Elasticsearch.")
        else:
            raise ValueError("Error: Unable to connect to Elasticsearch.")
        
        # Check the status of the trained model
        status = es_client.ml.get_trained_models_stats(model_id=elastic_search_model_id)
        if status["trained_model_stats"][0]["deployment_stats"]["state"] != "started":
            raise Exception("Model is downloaded but not ready to be deployed.")
        
        print(elastic_search_model_id, "is ready and deployed. This will be used to index the documents.")
        return es_client

    except Exception as e:
        raise ValueError(f"Error: {str(e)}")
    
async def create_and_check_async_elastic_client(es_connection, elastic_search_model_id):
    from elasticsearch import AsyncElasticsearch
    """
    Create an Elasticsearch client and check the status of a trained model.

    Parameters:
    - es_connection (dict): A dictionary containing the connection parameters for Elasticsearch.
    - elastic_search_model_id (str): The model ID for the Elasticsearch trained model.

    Returns:
    - es_client (Elasticsearch client): The Elasticsearch client instance if successful.
    """
    try:
        # Create the Elasticsearch client instance
        print("Reading from the connection..")
        ssl_certificate_content = es_connection.get('ssl_certificate') if es_connection.get('ssl_certificate') else ""
        cert_file_path = 'es_conn.crt'
        
        with open(cert_file_path, 'w') as file:
            file.write(ssl_certificate_content)
        
        # Create Elasticsearch client with appropriate authentication method
        if es_connection.get('api_key'):
            print("Connecting to Elastic Search using Elastic Search URL and API key.")
            es_client = AsyncElasticsearch(
                es_connection['url'],
                api_key=es_connection['api_key'],
                headers={'Content-Type': 'application/json'},
                ca_certs=cert_file_path,
                timeout=300, max_retries=10, retry_on_timeout=True
            )
        elif es_connection.get('username'):
            print("Connecting to Elastic Search using Elastic Search username and password.")
            es_client = AsyncElasticsearch(
                es_connection['url'],
                basic_auth=(es_connection['username'], es_connection['password']),
                headers={'Content-Type': 'application/json'},
                ca_certs=cert_file_path,
                timeout=300, max_retries=10, retry_on_timeout=True
            )
        else:
            raise ValueError("Error: No valid Elasticsearch connection parameters provided.")
        
        # Check if the Elasticsearch client is connected successfully
        if await es_client.ping():
            print("Successfully connected to Elasticsearch.")
        else:
            raise ValueError("Error: Unable to connect to Elasticsearch.")
        
        # Check the status of the trained model
        status = await es_client.ml.get_trained_models_stats(model_id=elastic_search_model_id)
        if status["trained_model_stats"][0]["deployment_stats"]["state"] != "started":
            raise Exception("Model is downloaded but not ready to be deployed.")
        
        print(elastic_search_model_id, "is ready and deployed. This will be used to index the documents.")
        return es_client

    except Exception as e:
        raise ValueError(f"Error: {str(e)}")

def connect_to_milvus_database(db_connection, parameters):
    import re
    from pymilvus import connections
    # Validate and set the default database if not provided
    db_connection['database'] = db_connection.get('database', 'default')
    
    # Define connection parameters
    connection_params = {
        'alias': db_connection['database'],
        'host': db_connection['host'],
        'port': db_connection['port'],
        'user': db_connection['username'],
        'password': db_connection['password'],
        'secure': True
    }

    milvus_credentials = {'db_name': db_connection['database'], 'password': db_connection['password'],
                                   'uri': "https://"+db_connection['host']+":"+db_connection['port'], "secure": True,
                                  'user': db_connection['username'] }

    # Handle SSL certificate if provided
    if 'ssl_certificate' in db_connection:
        ssl_certificate_content = db_connection.get('ssl_certificate', "")
        cert_file_path = 'milvus_conn.cert'
        with open(cert_file_path, 'w') as file:
            file.write(ssl_certificate_content)
        connection_params['server_pem_path'] = cert_file_path
        milvus_credentials['server_pem_path']=cert_file_path

    # Connect to Milvus if connection_type is 'milvus'
    milvus_client = connections.connect(**connection_params)

    print("Successfully connected to milvus database")

    # # Validate the vector_store_index_name using regular expression
    # regex = r'^[A-Za-z_]+[A-Za-z0-9_]*$' 
    
    # # Ensure the index name follows the regex pattern
    # if not re.match(regex, parameters['vector_store_index_name']):
    #     raise ValueError(f"ERROR: {parameters['vector_store_index_name']} name can only contain letters, numbers, and underscores.")

    return milvus_credentials

def connect_to_datastax(db_connection,parameters):
    """
    Connects to DataStax.

    Parameters:
    - parameters (dict): A dictionary containing the parameters for the keyspace creation.
    - db_connection (dict): A dictionary containing the database connection parameters.

    Returns:
    - session: The Cassandra session object else None if connection fails.
    - cluster: The Cassandra cluster object else None if connection fails.
    """
    from cassandra.cluster import Cluster # type: ignore
    from cassandra.auth import PlainTextAuthProvider
    from cassandra import OperationTimedOut, AuthenticationFailed
    from cassandra.query import SimpleStatement
    from ssl import SSLContext, PROTOCOL_TLSv1_2,CERT_NONE, CERT_REQUIRED

    cluster = None
    session = None

    try:
        auth_provider = PlainTextAuthProvider(
            db_connection['username'],
            db_connection['password']
        )
        # Path to your CA certificate file
        # Path to your CA certificate file
        #CA_CERTS_PATH = db_connection['']
        if 'ssl_certificate' in db_connection:
            ssl_certificate_content = db_connection.get('ssl_certificate', "")
            cert_file_path = 'datastax_conn.cert'
            with open(cert_file_path, 'w') as file:
                file.write(ssl_certificate_content)

            # Configure SSL options
            ssl_options = {
                'ca_certs': cert_file_path,
                'ssl_version': PROTOCOL_TLSv1_2, # Recommended for modern Cassandra versions
            }
            ssl_context = SSLContext(ssl_options)
            ssl_context.verify_mode = CERT_REQUIRED
        elif 'ssl' in db_connection:
            ssl_context = SSLContext(PROTOCOL_TLSv1_2)
            #ssl_context.load_verify_locations('your cert file')
            ssl_context.verify_mode = CERT_NONE
            cluster = Cluster(
                [db_connection['host']],
                port=db_connection['port'],
                ssl_context=ssl_context,
                auth_provider=auth_provider
            )
        else:
            cluster = Cluster(
                [db_connection['host']],
                port=db_connection['port'],
                auth_provider=auth_provider
            )
        session = cluster.connect()
        print("Successfully connected to Datastax.")

        # # Validate the vector_store_index_name using regular expression
        # regex = r'^[A-Za-z_]+[A-Za-z0-9_]*$' 
        
        # # Ensure the index name follows the regex pattern
        # if not re.match(regex, parameters['vector_store_index_name']):
        #     raise ValueError(f"ERROR: {parameters['vector_store_index_name']} name can only contain letters, numbers, and underscores.")

    except Exception as e:
        if session!=None:
            session.shutdown()
        if cluster!=None:
            cluster.shutdown()
        raise Exception(f"Failed to connect to DataStax: {e}")
    return session,cluster  

def check_datastax_ks_exists(db_connection, session):
    """
    Check if a keyspace in DataStax already exist or not.

    Parameters:
    - session: The Cassandra session object.
    - db_connection (dict): A dictionary containing the database connection parameters.

    Returns:
    - bool: True if the keyspace was created or already exists, False otherwise.
    """
    try:
        use_keyspace = db_connection.get("keyspace", None)
        if use_keyspace != None:
            # Query the system_schema.keyspaces table to check for the keyspace
            select_ks_query= session.prepare("SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = ?")
            rows = session.execute(select_ks_query,(use_keyspace,))

            if len(rows.current_rows) > 0:
                print(f"{use_keyspace} keyspace already exists")
                return True
            else:
                print(f"{use_keyspace} keyspace doesn't exist on cassandra server. Creating new keyspace")
                return False
        else:
            raise ValueError("ERROR: No keyspace provided in the db_connection parameters. Please provide a valid keyspace name.")
    except Exception as e:
        print(f"Error while checking keyspace '{use_keyspace}': {e}")
        raise Exception(f"Failed to check keyspace in DataStax: {e}")
        return None
    
def connect_to_astradb_using_cassandra(db_connection, parameters, scb_path=None):
    """
    Connects to AstraDB using Cassandra Driver.
    Parameters:
    - parameters (dict): A dictionary containing the parameters for the keyspace creation.
    - db_connection (dict): A dictionary containing the database connection parameters. 
    - scb_path (str, optional): The path to the secure connect bundle. If not provided, it will be taken from parameters.
    Returns:
    - session: The Cassandra session object else None if connection fails.
    - cluster: The Cassandra cluster object else None if connection fails.
    """

    session = None
    cluster = None
    from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, ProtocolVersion
    from cassandra.auth import PlainTextAuthProvider

    try:
        import os
        if scb_path is None:
            if 'astradb_scb_zip_filename' not in parameters or parameters['astradb_scb_zip_filename'] is None or parameters['astradb_scb_zip_filename']=='':
                raise ValueError("ERROR: No secure connect bundle filename provided in the parameters. Please provide a valid filename.")
            else:
                print("No secure connect bundle path provided, using the filename from parameters and assuming it is in the current working directory.")
            
            current_directory = os.getcwd()
            scb_path=os.path.join(current_directory, parameters["astradb_scb_zip_filename"])

        
        if not os.path.isfile(scb_path):
            raise ValueError(f"ERROR: Secure connect bundle file '{scb_path}' does not exist. Please provide a valid path.")

        cloud_config= {
            'secure_connect_bundle': scb_path,
            'connect_timeout': 30
        }
        #auth_provider=PlainTextAuthProvider("token", db_connection["astra_api_key"])
        auth_provider=PlainTextAuthProvider("token", db_connection["application_token"])
        profile = ExecutionProfile(request_timeout=30)
        cluster = Cluster(
            cloud=cloud_config,
            auth_provider=auth_provider,
            execution_profiles={EXEC_PROFILE_DEFAULT: profile},
            protocol_version=ProtocolVersion.V4
        )
        session = cluster.connect()
        print("Successfully connected to AstraDB aaS Datastax using Cassandra Driver.")

        # # Validate the vector_store_index_name using regular expression
        # regex = r'^[A-Za-z_]+[A-Za-z0-9_]*$' 

        # # Ensure the index name follows the regex pattern
        # if not re.match(regex, parameters['vector_store_index_name']):
        #     raise ValueError(f"ERROR: {parameters['vector_store_index_name']} name can only contain letters, numbers, and underscores.")

    except Exception as e:
        if session!=None:
            session.shutdown()
        if cluster!=None:
            cluster.shutdown()
        raise Exception(f"Failed to connect to AstraDBaaS DataStax: {e}")
    return session,cluster  

def get_iam_token(params):
    try:
        token_url = 'https://iam.cloud.ibm.com/identity/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                    'apikey':params["watsonx_ai_api_key"]
                    }
        token_res = requests.post(token_url, headers=headers, data=data)
        token = json.loads(token_res.text)['access_token']
    except Exception as e:
        token=''
        print('Error getting access token:', e)
        
    return token

def get_premium_retrieval(query, parameters, lakehouse_url=None, ai_bearer_token=None, headers=None):
    try:
        if lakehouse_url is None or lakehouse_url=='':
            print("No lakehouse_url provided, using default URL of Lakehouse IBM Cloud ToR region")
            lakehouse_url='https://console-ibm-cator.lakehouse.saas.ibm.com/api/v1/retrieval/search'
        
        if ai_bearer_token is not None and ai_bearer_token != '':
            token = ai_bearer_token
        else:
            print("No ai_bearer_token provided, using watsonx.ai API key to get IAM token for IBM Cloud")
            token = get_iam_token(parameters)
        
        if headers is None or headers=='':
            print("No headers provided, using default headers with IAM token for IBM Cloud")
            headers = {'Authorization': 'Bearer '+token,
                    'Content-Type': 'application/json' }
        ## below payload uses vector search only, sql search & llm inference is disabled. Please ignore those parameters
        data = {"query": query,
            "document_library_id": parameters["document_library_id"],
            "container_id": parameters["wxdata_project_id"],
            "container_type": "project",
            "searchConfig": [
                {
                    "type": "vector",
                    "enabled": True,
                    "limit": int(parameters["vectorsearch_top_n_results"])
                },
                {
                    "type": "sql",
                    "enabled": False
                }
            ],
                "search_inference_config": {
                "enabled": False,
                "inference_model_id": "meta-llama/llama-3-3-70b-instruct"
            },
            "provide_suggested_template": False}
        
        res = requests.post(lakehouse_url, headers=headers, json=data)
        print(res)
        #if res.status_code != 200:
        #    raise Exception(f"Error: Received status code {res.status_code} from the data premium: {res.text}")
        return res
    
    except Exception as e:
        print('Error retreiving documents from the data premium:',e)

def get_overlap(a,b):
    # returns maximum overlab (in characters) of suffix of a and prefix of b
    # less than 20 characters overlap are considered no overlap
    overlap = 0
    for n in range(min(len(a), len(b)), 20, -1):
        if a[-n:] == b[:n]:
            overlap = n
            break
    return overlap

def merge_documents(documents, document_source_field):
    length_reduction = 0
    if document_source_field == None or document_source_field == '':
        return documents, length_reduction
    document_source_path = document_source_field.split('.')
    get_source = lambda x: reduce(lambda a,i: a[i], document_source_path, x)

    documents_final = []

    # build sets of documents from same source
    try:
        documents = sorted(documents, key=get_source)

        document_sets = []

        i = -1
        for _document in documents:
            source = get_source(_document)

            # remove and save prefix
            if 'page_content' in _document:
                m = re.match('^(Document Title:.*?\n\s*Document Content:.*?\n\n)', _document['page_content'])
                if not m == None:
                    _document['page_content_prefix'] = m.groups()[0]
                    _document['page_content'] = _document['page_content'][len(m.groups()[0]):]
            
            if i==-1 or len(document_sets[i]) == 0 or not 'page_content' in _document or source == '' or not source == get_source(document_sets[i][0]):
                i=i+1
                document_sets.append([_document])
            else:
                document_sets[i].append(_document)
    except KeyError:
        # document source field not correct -> skip merging
        return documents, length_reduction

    # process sets of documents
    for _document_set in document_sets:

        dim = len(_document_set)
        if dim == 1:
            documents_final.append(_document_set[0])
            continue

        # (1) Build overlap matrix, position [d,a] holds maximum number of chars that suffix of d matches prefix of a (6 in example below)
        #         a  b  c  d
        #     -------------
        #     a | -  8  2  2
        #     b | 7  -  0  3
        #     c | 3  0  -  0
        #     d | 6  4  5  -
        # (2) Successively merge documents with maximum overlapping: a,b,c,d -> a-b,c,d -> d-a-b,c
        #     2 resulting (merged) documents: d-a-b, c

        # build (flatten) overlap matrix
        overlap_matrix =  [(get_overlap(_document_set[_y]['page_content'],_document_set[_x]['page_content']) if not _x==_y else -1) for _y in range(dim) for _x in range(dim)]
        doc_anchor = [x for x in range(dim)]

        # loop until no more overlaps
        while True:
            # find maximum overlap
            overlap = max(overlap_matrix)
            if not overlap > 0:
                break

            # merge documents
            prefix, suffix = divmod(overlap_matrix.index(overlap), dim)
            prefix_anchor = doc_anchor[prefix]
            _document_set[prefix_anchor]['page_content'] = _document_set[prefix_anchor]['page_content'] + _document_set[suffix]['page_content'][overlap:]
            try:
                _document_set[prefix_anchor]['score'] = max(_document_set[prefix_anchor]['score'], _document_set[suffix]['score'])
            except KeyError:
                # ignore missing score field
                pass
            _document_set[prefix_anchor]['chunk_count'] = \
                (_document_set[prefix_anchor]['chunk_count'] if 'chunk_count' in _document_set[prefix_anchor] else 1) + \
                (_document_set[suffix]['chunk_count'] if 'chunk_count' in _document_set[suffix] else 1)

            doc_anchor = [prefix_anchor if _anchor == suffix else _anchor for _anchor in doc_anchor]
            length_reduction = length_reduction + overlap

            # prefix cannot be a prefix again, suffix cannot be a suffix again
            for _y in range(dim):
                for _x in range(dim):
                    if _y == prefix or _x == suffix:
                        overlap_matrix[_y*dim + _x] = -1
            # avoid circles (current suffix must not become prefix of compound document)
            overlap_matrix[suffix*dim + prefix] = -1
           
        # add modified sets of documents:
        documents_final.extend([_document_set[_i] for _i in range(dim) if doc_anchor[_i] == _i])

    # reconstruct document prefixes
    for _document in documents_final:
        if 'page_content_prefix' in _document:
            _document['page_content'] = _document['page_content_prefix'] + _document['page_content']
            del(_document['page_content_prefix'])

    return documents_final, length_reduction

def remove_duplicate_records(split_docs):
    import hashlib
    from collections import Counter
    id_list=[]
    for doc in split_docs:
        id_list.append(hashlib.sha256((doc.page_content+'\nTitle: '+doc.metadata['title']+'\nUrl: '+doc.metadata['document_url']+'\nPage: '+doc.metadata['page_number']).encode()).hexdigest())  
    print(len(id_list) - len(set(id_list)),"duplicate documents found.")
    
    if (len(id_list) - len(set(id_list))) > 0:
        id_counter = Counter(id_list)
        exact_duplicate_ids = list([id_dup for id_dup in id_counter if id_counter[id_dup]>1])
        for dup_id in exact_duplicate_ids:
            dup_indexes = [i for i,val in enumerate(id_list) if val==dup_id][1:]
            for d_id in dup_indexes[::-1]:
                del split_docs[d_id]
                del id_list[d_id]
    return split_docs

def query_llm(client, deployment_id, question, query_filter):
    """
    Sends a question to Watsonx AI RAG deployment.
    Returns:
        tuple: (answer_str, documents, expert_response, log_id)
    """
    
    prompt_variables = {
        "question": question,
        "context": ""
    }

    logger.info(f"parameters['watsonx_max_tokens']: {parameters['watsonx_max_tokens']}")
    params = {
        "prompt_variables": prompt_variables,
        "decoding_method": "greedy",
        "max_new_tokens": int(parameters['watsonx_max_tokens'])
    }

    if query_filter:
        params["query_filter"] = query_filter

    response = client.deployments.generate(
        deployment_id=deployment_id,
        params=params
    )

    result = response["results"][0]
    documents = result.get("documents", {})
    hallucination_detection = result.get("Hallucination Detection", "NA")
    answer = {
        "response": result.get("generated_text", "").lstrip(),
        "Hallucination Detection": hallucination_detection
    }
    log_id = response.get("metadata", {}).get("id", "")
    expert_response = "No expert profile found for your question in the available documents."
    expert_result = result.get("expert_response")
    if expert_result is not None:
        experts_list = expert_result.get('body').get('recommended_top_experts')
        if len(experts_list) > 0:
            expert_response = experts_list[0]

    return answer, documents, expert_response, log_id

def query_llm_old(client, deployment_id, question,query_filter=None):
    payload = {"question": question}
    if query_filter:
        payload['query_filter'] = query_filter

    wx_result = client.deployments.run_ai_service(deployment_id, payload)
    documents = wx_result['result'].get('source_documents',{})
    hallucination_detection= wx_result['result'].get('Hallucination Detection',"NA")
    

    answer = {'response':wx_result['result'].get('response','').lstrip(),'Hallucination Detection':hallucination_detection}
    log_id = wx_result['result'].get('log_id','')
    

    expert_response = "No expert profile found for your question in the available documents."
    expert_result = wx_result['result'].get('expert_response')
    if expert_result is not None:
        experts_list = expert_result.get('body').get('recommended_top_experts')
        if len(experts_list) > 0:
            expert_response = experts_list[0]
    
    # End of expert profile section

    return answer,documents,expert_response, log_id

def display_results(question, documents, debug=False, answer=None, retreival_flag=False):
    
    display(Markdown(f'**Question:** {question}<br>**Answer:** {answer["response"]}<br>**Hallucination Detection:** {answer["Hallucination Detection"]}<br>'))

    if debug:
        m = f''
        if len(documents) > 0:
            m = f'{m}<table><thead><th>Title</th><th>Page Number</th><th>Source</th><th style="text-align: center;">Document</th><th>Score</th></thead><tbody>'
            if retreival_flag:
                m = f'{m}<table><thead><th>Doc Title</th><th>Chunk Seq Number</th><th>Source</th><th>Score</th></thead><tbody>'
            for d in documents:
                if retreival_flag:
                    m = f'{m}<tr><td>{d["metadata"]["source"]}</td><td>{d["metadata"]["chunk_seq"]}</td><td style="text-align: left;">{d["page_content"]}</td><td>{round(d["score"],2)}</td></tr>'
                else:
                    m = f'{m}<tr><td>{d["metadata"]["title"]}</td><td>{d["metadata"]["page_number"]}</td><td><a href="{d["metadata"]["document_url"]}">link</a></td><td style="text-align: left;">{d["page_content"]}</td><td>{round(d["score"],2)}</td></tr>'
            
            m = f'{m}</tbody></table><br><br><hr>'
        else:
            m = f'{m}No documents were used.'

        display(Markdown(m))

def qa_with_llm(client, deployment_id, retreival_flag=False):
    ui_title = widgets.HTML("<h2>QnA with RAG</h2>")

    question_textbox = widgets.Textarea(
        placeholder='Ask your question...',
        description='',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='60%', height='100px', margin='20px 0')
    )

    field_textbox = widgets.Text(
        placeholder='Field to filter (OPTIONAL)',
        description='Field:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='60%', margin='10px 0')
    )

    value_textbox = widgets.Text(
        placeholder='Value of the field (OPTIONAL)',
        description='Value:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='60%', margin='10px 0')
    )

    submit_button = widgets.Button(
        description='Submit',
        button_style='success',
        layout=widgets.Layout(width='60%', margin='10px 0')
    )

    result_output = widgets.Output()


    # Function to handle the submission
    def submit_question(button):
        global log_id
        user_question = question_textbox.value.strip()
        field = field_textbox.value.strip()
        value = value_textbox.value.strip()

        with result_output:
            clear_output(wait=True)

            if user_question:
                display(Markdown(f'**Question:** {user_question}<br>'))
                # Look up the answer in the Q&A deployment, using query_filter if provided
                query_filter = {}
                if field and value:
                    query_filter = {field: {"query": value}}

                answer, documents, expert_answer, log_id = query_llm(client, deployment_id, user_question, query_filter)
                
                table_content = ""
                if len(documents) > 0:
                    table_content = f'<table><thead><th>Title</th><th>Page Number</th><th>Source</th><th style="text-align: center;">Document</th><th>Score</th></thead><tbody>'
                    if retreival_flag:
                        table_content = f'<table><thead><th>Doc Title</th><th>Chunk Seq Number</th><th>Source</th><th style="text-align: center;">Document</th><th>Score</th></thead><tbody>'
                    for d in documents:
                        if retreival_flag:
                            table_content += f'<tr><td>{d["metadata"]["source"]}</td><td>{d["metadata"]["chunk_seq"]}</td>'
                        else:
                            table_content += f'<tr><td>{d["metadata"]["title"]}</td><td>{d["metadata"]["page_number"]}</td>'
                            table_content += f'<td><a href="{d["metadata"]["document_url"]}">link</a></td>'
                        
                        table_content += f'<td style="text-align: left;">{d["page_content"]}</td>'
                        table_content += f'<td>{round(d["score"], 2)}</td></tr>'

                    table_content += '</tbody></table><br><br><hr>'
                else:
                    table_content = 'No documents were used.'

                # Display the answer and table content
                display(HTML("<div class='response' style='color: green; animation: fadeIn 1s;'>"
                             f"<strong>Response:</strong> {answer['response']}<br></div>"))
                display(Markdown(f'**Hallucination Detection:** {answer["Hallucination Detection"]}<br>'))
                display(Markdown(table_content))

                # Display feedback section at the bottom
            else:
                # Display an error message with animation
                display(HTML("<div class='error' style='color: red; animation: shake 0.5s;'>"
                             "<strong>Please enter a question.</strong></div>"))


    # Attach the functions to the buttons' click events
    submit_button.on_click(submit_question)
    #feedback_button.on_click(submit_feedback)

    # Display the widgets
    display(HTML("<style>"
                 "@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }"
                 "@keyframes shake { 0%, 100% { transform: translateX(0); } 25%, 75% { transform: translateX(-5px); } 50% { transform: translateX(5px); } }"
                 ".response { margin-top: 10px; } .error { margin-top: 10px; }"
                 "</style>"))

    filters_header = widgets.HTML("<h3>Filters</h3>")

    return display(widgets.VBox([ui_title, question_textbox, filters_header, field_textbox, value_textbox, submit_button, result_output]))


# Sample Materials, provided under license.</a> <br>
# Licensed Materials - Property of IBM. <br>
# © Copyright IBM Corp. 2024, 2025. All Rights Reserved. <br>
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp. 
