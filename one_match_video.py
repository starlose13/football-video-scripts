# This code will simplify the provided script to generate a video for a single game instead of processing multiple games

import requests
import os
from dotenv import load_dotenv
import logging
import openai
import time
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
creatify_api_id = os.getenv('CREATIFY_API_ID')
creatify_api_key = os.getenv('CREATIFY_API_KEY')

logging.basicConfig(level=logging.INFO)

def fetch_single_game():
    url = "https://dataprovider.predipie.com/api/v1/ai/test/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")

    data = response.json()

    # Extract data for the first game
    match = data[0]
    match_data = {
        'home_team': match['home']['name'],
        'away_team': match['away']['name'],
        'a_team_odds': match['odds']['home'],
        'b_team_odds': match['odds']['away'],
        'league': match['competition']['name'],
        'start_time': match['start_time'],
        'stadium': match['venue']['name'] if match.get('venue') else 'Unknown Stadium'
    }

    return match_data

def generate_video_script(game_data):
    # Generate dynamic text based on the game data
    script = f"""
    Get ready for an exciting match! {game_data['home_team']} takes on {game_data['away_team']}
    at {game_data['stadium']} in the {game_data['league']}. The odds are in favor of {game_data['home_team']} 
    with {game_data['a_team_odds']} vs {game_data['away_team']}'s {game_data['b_team_odds']}. Don't miss the action!
    """
    return script

def generate_ai_shorts_preview(script):
    url = "https://api.creatify.ai/api/ai_shorts/preview/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "script": script,
        "aspect_ratio": "9x16",
        "style": "4K realistic"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        preview_data = response.json()
        logging.info(f"Preview generated successfully: {preview_data}")
        return preview_data['id']
    else:
        logging.error(f"Error generating preview: {response.text}")
        return None

def check_preview_status(preview_id):
    url = f"https://api.creatify.ai/api/ai_shorts/{preview_id}/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error checking preview status: {response.text}")
        return None

def render_ai_shorts_video(preview_id):
    url = f"https://api.creatify.ai/api/ai_shorts/{preview_id}/render/"
    headers = {
        "X-API-ID": creatify_api_id,
        "X-API-KEY": creatify_api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"Video rendering started for preview ID: {preview_id}")
        return True
    else:
        logging.error(f"Error rendering video: {response.text}")
        return False

def send_to_creatify(video_script):
    preview_id = generate_ai_shorts_preview(video_script)

    if preview_id:
        start_time = time.time()
        timeout = 900

        while True:
            preview_data = check_preview_status(preview_id)
            if preview_data and preview_data['status'] == 'done':
                logging.info(f"Preview generated: {preview_data}")
                break
            logging.info("Waiting for preview to be generated...")

            if time.time() - start_time > timeout:
                logging.error("Preview generation timeout.")
                return None

            time.sleep(10)

        if render_ai_shorts_video(preview_id):
            while True:
                preview_data = check_preview_status(preview_id)
                if preview_data and preview_data['status'] == 'done':
                    logging.info(f"Video render completed: {preview_data}")
                    return preview_data['video_output']

                logging.info("Waiting for video rendering to complete...")

                if time.time() - start_time > timeout:
                    logging.error("Video rendering timeout.")
                    return None

                time.sleep(10)
        else:
            logging.error("Error starting video rendering.")
            return None
    else:
        logging.error("Error generating video preview.")
        return None

def main():
    game_data = fetch_single_game()
    video_script = generate_video_script(game_data)
    video_output = send_to_creatify(video_script)

    if video_output:
        logging.info(f"Video ready: {video_output}")
        print(f"Video for {game_data['home_team']} vs {game_data['away_team']} is ready: {video_output}")
    else:
        logging.error(f"Error generating video for {game_data['home_team']} vs {game_data['away_team']}.")

if __name__ == "__main__":
    main()
