import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("AZURE_CONNECTION_STRING")
container_name = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)

def upload_file_to_azure(file, filename):
    container_client = blob_service_client.get_container_client(container_name)

    blob_client = container_client.get_blob_client(filename)

    blob_client.upload_blob(file, overwrite=True)

    return blob_client.url