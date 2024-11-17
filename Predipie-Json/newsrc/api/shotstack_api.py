import requests
from config.config import SHOTSTACK_API_KEY
from utils.json_saver import JsonSaver

class ShotstackAPI:
    @staticmethod
    def upload_video(video_url):
        render_url = "https://api.shotstack.io/v1/render"
        headers = {"x-api-key": SHOTSTACK_API_KEY, "Content-Type": "application/json"}

        timeline = {
            "background": "#000000",
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {"type": "video", "src": video_url},
                            "fit": "contain",
                            "start": 0,
                            "length": "auto",
                        }
                    ]
                }
            ]
        }
        payload = {
            "timeline": timeline,
            "output": {"format": "mp4", "resolution": "hd", "fps": 30}
        }

        response = requests.post(render_url, headers=headers, json=payload)
        if response.status_code == 201:
            render_id = response.json().get("response", {}).get("id")
            print("Render request submitted and queued. Render ID:", render_id)
            saver = JsonSaver()
            saver.save_to_json({"render_id": render_id}, "shotstack_render_id.json")
            return render_id
        else:
            print("Failed to submit render request:", response.status_code, response.text)
            return None

    @staticmethod
    def check_render_status(render_id):
        status_url = f"https://api.shotstack.io/v1/render/{render_id}"
        headers = {"x-api-key": SHOTSTACK_API_KEY}

        response = requests.get(status_url, headers=headers)
        if response.status_code == 200:
            status = response.json().get("response", {}).get("status")
            url = response.json().get("response", {}).get("url")
            return status, url
        else:
            print("Failed to check render status:", response.status_code, response.text)
            return None, None
