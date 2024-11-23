import os
import json
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Load environment variables
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
creatify_api_id = os.getenv("CREATIFY_API_ID")
creatify_api_key = os.getenv("CREATIFY_API_KEY")
START_AFTER = os.getenv("START_AFTER")
OUTPUT_FOLDER = f"{START_AFTER}_json_match_output_folder/uploaded_video_source_ids"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Retrieve the two most recent videos from Creatify
def get_latest_creatify_videos():
    url = "https://api.creatify.ai/api/lipsyncs/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        creatify_data = response.json()
        if creatify_data and isinstance(creatify_data, list):
            # Sort videos by 'created_at' in descending order
            sorted_videos = sorted(
                creatify_data,
                key=lambda x: datetime.fromisoformat(x.get("created_at", "")),
                reverse=True
            )
            # Get the two most recent videos
            latest_videos = sorted_videos[:2]
            return [
                {"url": video.get("output"), "id": video.get("id")}
                for video in latest_videos if video.get("output")
            ]
        else:
            print("No videos found in Creatify response.")
    else:
        print("Failed to retrieve data from Creatify:", response.status_code, response.text)
    return []

# Upload video URL to Shotstack and return the render ID
def upload_video_to_shotstack(video_url):
    render_url = "https://api.shotstack.io/v1/render"
    headers = {"x-api-key": shotstack_api_key, "Content-Type": "application/json"}

    # Define the video timeline for rendering
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
        return render_id
    else:
        print("Failed to submit render request:", response.status_code, response.text)
        return None

# Check render status and retrieve the final video URL once the rendering is complete
def check_render_status(render_id):
    status_url = f"https://api.shotstack.io/v1/render/{render_id}"
    headers = {"x-api-key": shotstack_api_key}

    response = requests.get(status_url, headers=headers)
    if response.status_code == 200:
        status = response.json().get("response", {}).get("status")
        url = response.json().get("response", {}).get("url")
        return status, url
    else:
        print("Failed to check render status:", response.status_code, response.text)
        return None, None

# Save data to JSON
def save_to_json(data, filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    with open(filepath, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {filepath}")

# Main execution
def main():
    # Retrieve the two most recent Creatify videos
    videos = get_latest_creatify_videos()
    if len(videos) < 2:
        print("Less than two videos available from Creatify; cannot proceed.")
        return

    uploaded_videos = []

    # Upload each video to Shotstack
    for i, video in enumerate(videos, start=1):
        print(f"Processing video {i}: {video['url']}")
        render_id = upload_video_to_shotstack(video["url"])
        if render_id:
            # Check rendering status periodically
            while True:
                status, final_video_url = check_render_status(render_id)
                if status == "done":
                    print(f"Render complete for video {i}. Video URL:", final_video_url)
                    uploaded_videos.append({
                        "creatify_video_id": video["id"],
                        "shotstack_render_id": render_id,
                        "shotstack_video_url": final_video_url
                    })
                    break
                elif status == "failed":
                    print(f"Render failed for video {i}.")
                    break
                else:
                    print(f"Render status for video {i}: {status}")
                    time.sleep(10)  # Wait 10 seconds before checking again
        else:
            print(f"Failed to upload video {i} to Shotstack.")

    # Save the results to JSON
    save_to_json(uploaded_videos, "uploaded_video_source_ids.json")


if __name__ == "__main__":
    main()
