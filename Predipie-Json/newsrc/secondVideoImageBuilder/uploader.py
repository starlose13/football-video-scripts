import requests
from .configAPI import Config

class ShotstackUploader:
    def __init__(self):
        self.api_key = Config.shotstack_api_key
        self.uploaded_files = {}

    def get_signed_url(self):
        signed_url_request_url = "https://api.shotstack.io/ingest/v1/upload"
        headers = {"Accept": "application/json", "x-api-key": self.api_key}
        response = requests.post(signed_url_request_url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {}).get("attributes", {})
            return data.get("url"), data.get("id")
        print("Failed to obtain signed URL:", response.status_code, response.text)
        return None, None

    def upload_image(self, image_path, file_name):
        signed_url, source_id = self.get_signed_url()
        if not signed_url:
            print(f"Skipping upload for {image_path}")
            return None

        with open(image_path, "rb") as file:
            upload_response = requests.put(signed_url, data=file)
            if upload_response.status_code == 200:
                print(f"Image uploaded successfully for {image_path}")
                self.uploaded_files[file_name] = source_id
                return source_id
            print(f"Failed to upload {image_path}:", upload_response.status_code, upload_response.text)
        return None

    def check_upload_status(self, source_id):
        """Check the status of the uploaded image by source ID."""
        status_url = f"https://api.shotstack.io/ingest/v1/sources/{source_id}"
        headers = {"Accept": "application/json", "x-api-key": self.api_key}
        status_response = requests.get(status_url, headers=headers)
        if status_response.status_code == 200:
            attributes = status_response.json().get("data", {}).get("attributes", {})
            return attributes.get("status"), attributes.get("source")
        print("Failed to retrieve upload status:", status_response.status_code, status_response.text)
        return None, None
