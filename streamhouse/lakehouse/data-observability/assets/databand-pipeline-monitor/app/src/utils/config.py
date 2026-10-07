"""
Configuration loader for the Databand Pipeline Monitor service.
"""
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "databand": {
        "url": os.getenv("DATABAND_URL", ""),
        "access_token": os.getenv("DATABAND_ACCESS_TOKEN", ""),
    },
    "ibm_cloud": {
        "api_key": os.getenv("IBM_API_KEY", ""),
        "iam_url": os.getenv("IBM_IAM_URL", "https://iam.cloud.ibm.com/identity/token"),
    },
    "cos": {
        "endpoint": os.getenv("COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"),
        "api_key": os.getenv("COS_API_KEY", ""),
        "instance_crn": os.getenv("COS_INSTANCE_CRN", ""),
        "bucket": os.getenv("COS_BUCKET", "databand-logs"),
    },
    "server": {
        "url": os.getenv("SERVER_URL", "http://localhost:8080"),
        "rest_api_key": os.getenv("REST_API_KEY", ""),
    },
    "notifications": {
        "alert_email": os.getenv("ALERT_EMAIL", ""),
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL", ""),
    },
}
