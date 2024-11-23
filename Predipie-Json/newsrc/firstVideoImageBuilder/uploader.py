# main_upload.py
import os
import requests
from config.config import SHOTSTACK_API_KEY
class ShotstackUploader:
    def __init__(self, api_key):
        self.api_key = api_key
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
        """
        بررسی وضعیت آپلود تصویر در Shotstack.
        """
        status_url = f"https://api.shotstack.io/ingest/v1/sources/{source_id}"
        headers = {"Accept": "application/json", "x-api-key": self.api_key}
        status_response = requests.get(status_url, headers=headers)
        
        if status_response.status_code == 200:
            attributes = status_response.json().get("data", {}).get("attributes", {})
            return attributes.get("status"), attributes.get("source")
        
        print("Failed to retrieve upload status:", status_response.status_code, status_response.text)
        return None, None

    def upload_images_in_folder(self, folder_path="./ingested_files"):

        for file_name in os.listdir(folder_path):
            if file_name.endswith((".jpg", ".png")):
                image_path = os.path.join(folder_path, file_name)
                source_id = self.upload_image(image_path, file_name)
                if source_id:
                    status, source_url = self.check_upload_status(source_id)
                    print(f"Upload status for {file_name}: {status}")
                    if status == "ready":
                        print(f"Image {file_name} is ready at {source_url}")

# نحوه استفاده از کد
if __name__ == "__main__":
    api_key = SHOTSTACK_API_KEY  
    uploader = ShotstackUploader(api_key)
    uploader.upload_images_in_folder()  