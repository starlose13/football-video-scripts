import requests
import os
import logging
from dotenv import load_dotenv
import time
import certifi

# Load environment variables from .env file
load_dotenv()

# Setup Creatify API credentials
creatify_api_id = os.getenv('CREATIFY_API_ID')
creatify_api_key = os.getenv('CREATIFY_API_KEY')

# Check if API credentials are set
if not creatify_api_id or not creatify_api_key:
    raise ValueError("Creatify API credentials not found! Set them in the .env file")

# Function to queue AI Avatar lipsync task with a simple test script
def generate_ai_avatar_lipsync(script, creator="5021bec0-f33f-43e6-b0e3-1cb7f76003c6", aspect_ratio="1:1"):
    url = "https://api.creatify.ai/api/lipsyncs/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": script,  # The simple video script for testing
        "creator": creator,
        "aspect_ratio": aspect_ratio
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=certifi.where())
        if response.status_code == 200:
            avatar_data = response.json()
            logging.info(f"Lipsync task queued successfully: {avatar_data}")
            return avatar_data['id']  # Return the lipsync ID
        else:
            logging.error(f"Error queuing lipsync task: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in lipsync task queueing: {e}")
        return None

# Function to check the status of the AI Avatar lipsync video
def check_ai_avatar_status(lipsync_id):
    url = f"https://api.creatify.ai/api/lipsyncs/{lipsync_id}/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            lipsync_data = response.json()
            logging.info(f"Lipsync video status: {lipsync_data['status']}")
            return lipsync_data
        else:
            logging.error(f"Error checking lipsync status: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in checking lipsync status: {e}")
        return None

# Function to send the test script to AI Avatar and monitor the result
def send_to_ai_avatar(video_script):
    lipsync_id = generate_ai_avatar_lipsync(video_script)
    if lipsync_id:
        start_time = time.time()
        timeout = 900  # Set a timeout of 15 minutes

        while True:
            lipsync_data = check_ai_avatar_status(lipsync_id)
            if lipsync_data:
                if lipsync_data['status'] == 'done':
                    logging.info(f"Lipsync video generated: {lipsync_data}")
                    return lipsync_data['output']  # Return the video URL
                elif lipsync_data['status'] == 'failed':
                    logging.error(f"Lipsync generation failed: {lipsync_data.get('failed_reason', 'Unknown reason')}")
                    return None
                else:
                    logging.info(f"Video is still in progress. Status: {lipsync_data['status']}")
            else:
                logging.error("Failed to retrieve lipsync data.")
                return None

            if time.time() - start_time > timeout:
                logging.error("Lipsync video generation timeout.")
                return None  # Return early to avoid infinite wait

            time.sleep(30)  # Poll every 30 seconds

    else:
        logging.error("Error queuing AI Avatar video.")
        return None

# Main function to test with a simple script
def main():
    logging.basicConfig(level=logging.INFO)

    # Simple test script to send to the AI Avatar
    test_script = "Al-Batin faces Al Zulfi in a tight match. Odds favor Al-Batin, but anything can happen!"

    # Send the script to AI Avatar and generate a video
    video_url = send_to_ai_avatar(test_script)

    if video_url:
        logging.info(f"Video ready: {video_url}")
        print(f"Video for the test script is ready: {video_url}")
    else:
        logging.error("Error generating video for the test script.")

if __name__ == "__main__":
    main()
