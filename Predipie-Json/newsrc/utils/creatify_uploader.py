import requests
import time
import logging


class CreatifyUploader:
    def __init__(self, api_id: str, api_key: str):
        self.api_id = api_id
        self.api_key = api_key
        self.base_url = "https://api.creatify.ai/api/lipsyncs/"
        self.headers = {
            "X-API-ID": self.api_id,
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def create_video(self, narration_text: str, creator_id: str, aspect_ratio: str = "1:1") -> str:
        payload = {
            "text": narration_text,
            "creator": creator_id,
            "aspect_ratio": aspect_ratio
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            lipsync_data = response.json()
            lipsync_id = lipsync_data.get("id")
            logging.info(f"Video generation initiated. Lipsync ID: {lipsync_id}")
            return self._check_video_status(lipsync_id)
        except requests.RequestException as e:
            print(f"Creatify API error: {e}")
            print(f"Response content: {response.text}")
            return None

    def _check_video_status(self, lipsync_id: str) -> str:
        """Polls the Creatify API to check the status of the video."""
        status_url = f"{self.base_url}{lipsync_id}/"
        while True:
            try:
                status_response = requests.get(status_url, headers=self.headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                status = status_data.get("status")

                if status == "done":
                    video_url = status_data.get("output")
                    logging.info(f"Video generation completed. Download your video at: {video_url}")
                    return video_url
                elif status in ["failed", "error"]:
                    logging.error(f"Video generation failed with status: {status}")
                    return None

                logging.info("Video generation in progress. Checking again in 10 seconds...")
                time.sleep(10)
            except requests.RequestException as e:
                logging.error(f"Failed to check video status: {e}")
                return None
