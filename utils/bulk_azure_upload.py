import os
from utils.azure_storage import upload_file_to_azure
from django.conf import settings

def upload_all_documents():
    documents_folder = os.path.join(settings.BASE_DIR, "documents")

    for filename in os.listdir(documents_folder):

        file_path = os.path.join(documents_folder, filename)

        if os.path.isfile(file_path):

            print(f"Uploading {filename}")

            with open(file_path, "rb") as f:
                upload_file_to_azure(f, filename)