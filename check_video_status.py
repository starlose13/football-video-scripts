import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

creatify_api_id = os.getenv('CREATIFY_API_ID')
creatify_api_key = os.getenv('CREATIFY_API_KEY')

if not creatify_api_id or not creatify_api_key:
    raise ValueError("Creatify API credentials not found! Set them in the .env file.")

# Function to check the status of the video
def check_video_status(video_id):
    status_url = f"https://api.creatify.ai/api/link_to_videos/{video_id}/"
    headers = {
        'X-API-ID': creatify_api_id,
        'X-API-KEY': creatify_api_key
    }

    status_response = requests.get(status_url, headers=headers)
    
    if status_response.status_code == 200:
        video_status = status_response.json().get('status', 'unknown')
        video_output = status_response.json().get('video_output', None)
        
        print(f"Current status of video {video_id}: {video_status}")
        
        if video_status == 'done':
            print(f"Video is ready. You can download or view it here: {video_output}")
            return video_output
        else:
            print(f"Video is still processing, current status: {video_status}")
            return None
    else:
        print(f"Error checking video status: {status_response.content}")
        return None

if __name__ == "__main__":
    # Replace with your video ID to check
    video_id = input("Enter the Video ID: ").strip()

    # Call the function to check status
    video_output = check_video_status(video_id)

    if video_output:
        print(f"Video ready at: {video_output}")
    else:
        print("Video is still processing.")
