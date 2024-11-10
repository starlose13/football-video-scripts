import os
import json
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Load environment variables
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
shotstack_env = os.getenv("SHOTSTACK_ENVIRONMENT", "stage")
creatify_api_id = os.getenv("CREATIFY_API_ID")
creatify_api_key = os.getenv("CREATIFY_API_KEY")

# Retrieve the latest video from Creatify based on the newest 'created_at' timestamp
def get_latest_creatify_video_url():
    url = "https://api.creatify.ai/api/lipsyncs/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        creatify_data = response.json()
        if creatify_data and isinstance(creatify_data, list):
            # Sort videos by 'created_at' date, then get the latest one
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

# Save URL or render ID to a JSON file
def save_to_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {filename}")

# Upload video URL to Shotstack and return the render ID
def upload_video_to_shotstack(video_url):
    render_url = f"https://api.shotstack.io/{shotstack_env}/render"
    headers = {"x-api-key": shotstack_api_key, "Content-Type": "application/json"}

    # Define the video timeline for rendering
    timeline = {
        "background": "#000000",
        "tracks": [
            {
                "clips": [
                    {"asset": {"type": "video", "src": video_url}, "start": 0, "length": "auto", "transition": {"in": "fade", "out": "fade"}}
                ]
            }
        ]
    }
    payload = {
        "timeline": timeline,
        "output": {
            "format": "mp4",
            "resolution": "hd",
            "fps": 30
        }
    }

    response = requests.post(render_url, headers=headers, json=payload)
    if response.status_code == 201:
        render_id = response.json().get("response", {}).get("id")
        print("Render request submitted and queued. Render ID:", render_id)
        save_to_json({"render_id": render_id}, "shotstack_render_id.json")
        return render_id
    else:
        print("Failed to submit render request:", response.status_code, response.text)
        return None

# Check render status and retrieve the final video URL once the rendering is complete
def check_render_status(render_id):
    status_url = f"https://api.shotstack.io/{shotstack_env}/render/{render_id}"
    headers = {"x-api-key": shotstack_api_key}

    response = requests.get(status_url, headers=headers)
    if response.status_code == 200:
        status = response.json().get("response", {}).get("status")
        url = response.json().get("response", {}).get("url")
        return status, url
    else:
        print("Failed to check render status:", response.status_code, response.text)
        return None, None

# Main execution
video_url = get_latest_creatify_video_url()
if video_url:
    render_id = upload_video_to_shotstack(video_url)
    if render_id:
        # Check the rendering status periodically
        while True:
            status, final_video_url = check_render_status(render_id)
            if status == "done":
                print("Render complete. Video URL:", final_video_url)
                save_to_json({"shotstack_video_url": final_video_url}, "shotstack_video_url.json")
                break
            elif status == "failed":
                print("Render failed.")
                break
            else:
                print("Render status:", status)
                time.sleep(10)  # Wait 10 seconds before checking again
else:
    print("No valid video URL available from Creatify; cannot proceed with Shotstack rendering.")
