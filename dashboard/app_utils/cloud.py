""
import os
from io import BytesIO

from google.oauth2 import service_account
from google.cloud import storage
from datetime import datetime, timezone, timedelta
from google.cloud.storage import Client
from dotenv import load_dotenv

from app_config import app_dir

def gc_credentials_dict() -> dict:
    load_dotenv(app_dir / ".env")

    private_credentials = {
        "private_key_id": os.getenv("SP_PRIVATE_KEY_ID"),
        "private_key": os.getenv("SP_PRIVATE_KEY"),
        "client_email": os.getenv("SP_CLIENT_EMAIL"),
        "client_id": os.getenv("SP_CLIENT_ID"),
    }

    for key, value in private_credentials.items():
        if value is None:
            raise ValueError(f"Environment variable {key} is not set.")

    credentials = {
        "type": "service_account",
        "project_id": "sy-bat",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/shinyapp%40sy-bat.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }
    credentials.update(private_credentials)

    return credentials




def generate_signed_url(bucket_name: str, blob_name: str, expiration_time_seconds: int = 60) -> str:
    #Define the service account key and project id
    gc_credentials = gc_credentials_dict()
    project_id= gc_credentials["project_id"]

    #create a credential to initialize the Storage client
    credentials = service_account.Credentials.from_service_account_info(gc_credentials)
    client = storage.Client(project_id,credentials)

    #Get the time in UTC
    ini_time_for_now = datetime.now(timezone.utc)

    #Set the expiration time
    expiration_time = ini_time_for_now + timedelta(seconds=expiration_time_seconds) 

    #Initialize the bucket and blob
    bucket = client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)

    #Get the signed URL
    url = blob.generate_signed_url(expiration=expiration_time)
    return url


class CloudBucket:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        credentials = gc_credentials_dict()
        self.project_id = credentials["project_id"]
        self.client = Client(credentials=service_account.Credentials.from_service_account_info(credentials))
        self.bucket = self.client.bucket(self.bucket_name)

    def get_blob_bytes(self, blob_name: str):
        blob = self.bucket.blob(blob_name)
        return BytesIO(blob.download_as_bytes())
