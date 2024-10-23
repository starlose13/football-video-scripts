# Function to check the status of the Synthesia video
import logging
import os
from urllib import request

from AIAvatarAPI import fetch_odds_rank_and_last_5_games, generate_video_script
from DemoSynthesia import send_to_synthesia
from ImageGenerator import generate_match_image


def check_synthesia_video_status(video_id):
    url = f"https://api.synthesia.io/v2/videos/{video_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('SYNTHESIA_API_KEY')}"
    }
    
    try:
        response = request.get(url, headers=headers)
        if response.status_code == 200:
            video_data = response.json()
            logging.info(f"Synthesia video status: {video_data['status']}")
            return video_data  # This contains the video status and download URL when done
        else:
            logging.error(f"Error checking Synthesia video status: {response.text}")
            return None
    except request.exceptions.RequestException as e:
        logging.error(f"Error in checking Synthesia video status: {e}")
        return None

# Main function to execute the script
def main():
    # Fetch the first match data
    match_data = fetch_odds_rank_and_last_5_games()

    home_team = match_data['home_team']
    away_team = match_data['away_team']

    # Generate the match image
    background_image_path = generate_match_image(match_data, 1)  # Generate image for the match

    # Generate the video script using the precomputed prediction result and row number
    video_script = generate_video_script(match_data, match_data['prediction_result'], match_data['row_number'])

    # Log the generated script
    print(f"Generated Video Script for {home_team} vs {away_team}:\n", video_script)

    # Send the script to Synthesia and generate a video
    video_id = send_to_synthesia(video_script, home_team, away_team, background_image_path)

    if video_id:
        logging.info(f"Video request sent. Video ID: {video_id}")
        print(f"Video request sent. Video ID: {video_id}")

        # Check the status of the video every 30 seconds until it is done or failed
        import time
        timeout = 1200  # Timeout after 20 minutes
        start_time = time.time()

        while True:
            video_data = check_synthesia_video_status(video_id)
            if video_data:
                if video_data['status'] == 'done':
                    logging.info(f"Video ready: {video_data['downloadUrl']}")
                    print(f"Video ready! Download URL: {video_data['downloadUrl']}")
                    break
                elif video_data['status'] == 'failed':
                    logging.error(f"Video generation failed: {video_data.get('errorMessage', 'Unknown reason')}")
                    break
                else:
                    logging.info(f"Video is still being processed. Current status: {video_data['status']}")
                    time.sleep(30)  # Wait 30 seconds before checking again

            if time.time() - start_time > timeout:
                logging.error("Video generation timed out.")
                break
    else:
        logging.error(f"Error generating video for {home_team} vs {away_team}.")
