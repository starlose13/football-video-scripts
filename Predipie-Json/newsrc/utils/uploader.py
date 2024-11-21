import requests
import os
import json
from config.config import SHOTSTACK_API_KEY


class ShotstackUploader:
    def __init__(self):
        self.api_key = SHOTSTACK_API_KEY

    def get_signed_url(self):
        signed_url_request_url = "https://api.shotstack.io/ingest/v1/upload"
        headers = {"Accept": "application/json", "x-api-key": self.api_key}
        try:
            response = requests.post(signed_url_request_url, headers=headers)
            response.raise_for_status()
            data = response.json().get("data", {}).get("attributes", {})
            return data.get("url"), data.get("id")
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining signed URL: {e}")
            return None, None

    def upload_image(self, image_path, file_name):
        signed_url, source_id = self.get_signed_url()
        if not signed_url:
            print(f"Skipping upload for {image_path}. Signed URL not available.")
            return None

        try:
            with open(image_path, "rb") as file:
                upload_response = requests.put(signed_url, data=file)
                upload_response.raise_for_status()
                print(f"Image uploaded successfully: {image_path}")
                return source_id
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload {image_path}: {e}")
            return None

    def upload_images_in_folder(self, folder_path, output_json_path):
        """
        Upload all images in the specified folder and save source IDs to a JSON file.
        
        Args:
            folder_path (str): Path to the folder containing images to upload.
            output_json_path (str): Path to save the JSON file with source IDs.

        Returns:
            dict: A dictionary of file names and their respective source IDs.
        """
        if not os.path.exists(folder_path):
            print(f"Folder does not exist: {folder_path}")
            return {}

        uploaded_files = {}
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jpg"):
                image_path = os.path.join(folder_path, file_name)
                source_id = self.upload_image(image_path, file_name)
                if source_id:
                    uploaded_files[file_name] = source_id

        # Save uploaded files to JSON
        if uploaded_files:
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
            with open(output_json_path, "w") as json_file:
                json.dump(uploaded_files, json_file, indent=4)
            print(f"Uploaded files and their source IDs saved to {output_json_path}")
        else:
            print("No images were uploaded successfully.")

        return uploaded_files
