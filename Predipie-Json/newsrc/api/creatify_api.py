import requests
from datetime import datetime
from config import CREATIFY_API_ID, CREATIFY_API_KEY

class CreatifyAPI:
    @staticmethod
    def get_latest_video_url():
        url = "https://api.creatify.ai/api/lipsyncs/"
        headers = {
            "X-API-ID": CREATIFY_API_ID,
            "X-API-KEY": CREATIFY_API_KEY
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            creatify_data = response.json()
            if creatify_data and isinstance(creatify_data, list):
                latest_video = max(creatify_data, key=lambda x: datetime.fromisoformat(x.get("created_at", "")))
                output_url = latest_video.get("output")
                if output_url:
                    print("Latest Creatify video output URL retrieved:", output_url)
                    return output_url
                else:
                    print("No output URL found for the latest video.")
        else:
            print("Failed to retrieve data from Creatify:", response.status_code, response.text)
        return None
