import os
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from github import Github
import base64
from dotenv import load_dotenv

from AIAvatarAPI import calculate_points, calculate_points_summary, calculate_rank_difference, classify_a_points, classify_a_team, classify_b_points, classify_b_team, generate_result, generate_video_script

# Load environment variables from .env file
load_dotenv()

# Function to fetch odds, rank, and last 5 games for both teams
def fetch_odds_rank_and_last_5_games():
    url = "https://dataprovider.predipie.com/api/v1/ai/test/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")
    
    data = response.json()

    for match in data:
        match_id = match['id']
        home_team_name = match['home']['name']
        away_team_name = match['away']['name']
        home_team_logo = match['home']['logo']
        away_team_logo = match['away']['logo']
        home_odds = match['odds']['home']
        away_odds = match['odds']['away']
        league = match['competition']['name']
        start_time_str = match['start_time']
        stadium = match['venue']['name'] if match.get('venue') and match['venue'].get('name') else 'Unknown Stadium'
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
        day = start_time.strftime("%A")
        time = start_time.strftime("%H:%M")


        if home_odds < away_odds:
            a_team_name, b_team_name = home_team_name, away_team_name
            a_odds, b_odds = home_odds, away_odds
        else:
            a_team_name, b_team_name = away_team_name, home_team_name
            a_odds, b_odds = away_odds, home_odds

        team_a_last_5_games = match['team_related_match'][0]['five_previous_matches']
        team_b_last_5_games = match['team_related_match'][1]['five_previous_matches']
        a_wins, a_draws, a_losses = calculate_points_summary(team_a_last_5_games)
        b_wins, b_draws, b_losses = calculate_points_summary(team_b_last_5_games)

        team_a_rank = match['team_related_match'][0]['rank']
        team_b_rank = match['team_related_match'][1]['rank']

        a_points = calculate_points(team_a_last_5_games)
        b_points = calculate_points(team_b_last_5_games)
        a_recent_group = classify_a_points(a_points)
        b_recent_group = classify_b_points(b_points)
        rank_diff = calculate_rank_difference(team_a_rank, team_b_rank)

        a_team = classify_a_team(a_odds)
        b_team = classify_b_team(b_odds)

        prediction_result, row_number = generate_result(a_team, b_team, a_recent_group, b_recent_group, rank_diff)

        game_data = {
            'match_id': match_id,
            'home_team': home_team_name,
            'away_team': away_team_name,
            'home_team_logo': home_team_logo,
            'away_team_logo': away_team_logo,
            'a_team_name': a_team_name,
            'b_team_name': b_team_name,
            'a_team_odds': a_odds,
            'b_team_odds': b_odds,
            'team_a_last_5': team_a_last_5_games,
            'team_b_last_5': team_b_last_5_games,
            'team_a_rank': team_a_rank,
            'team_b_rank': team_b_rank,
            'a_wins': a_wins,
            'a_draws': a_draws,
            'a_losses': a_losses,
            'b_wins': b_wins,
            'b_draws': b_draws,
            'b_losses': b_losses,
            'league': league,
            'stadium': stadium,
            'day': day,
            'time': time,
            'prediction_result': prediction_result,
            'row_number': row_number
        }

        return game_data

# Function to generate match image
def generate_match_image(match_data, match_number):
    img = Image.open("./assets/match-template.png")
    draw = ImageDraw.Draw(img)

    font_path = "arial.ttf"
    font_team = ImageFont.truetype(font_path, 32)
    font_league = ImageFont.truetype(font_path, 30)
    font_details = ImageFont.truetype(font_path, 32)

    home_team_name = match_data['home_team']
    away_team_name = match_data['away_team']
    home_team_logo = match_data['home_team_logo']
    away_team_logo = match_data['away_team_logo']
    league = match_data['league']
    stadium = match_data['stadium']
    day = match_data['day']
    time = match_data['time']

    draw.text((750, 472), home_team_name, fill="white", font=font_team)
    draw.text((img.width - 630, 472), away_team_name, fill="white", font=font_team)
    draw.text((img.width - 460, 472), home_team_logo, fill="white", font=font_team)
    draw.text((img.width - 3200, 472), away_team_logo, fill="white", font=font_team)
    draw.text((img.width - 1140, 425), league, fill="white", font=font_league)
    draw.text((img.width - 1140, 845), f"{day} {time}", fill="white", font=font_details)
    draw.text((img.width - 1140, 950), stadium, fill="white", font=font_details)

    output_path = f"output_{home_team_name}_vs_{away_team_name}.png"
    img.save(output_path)
    print(f"Generated image for match {match_number} at {output_path}")
    return output_path  # Return the local image path

# Function to upload image to GitHub and get the public URL
def upload_image_to_github(image_path, folder, file_name):
    token = os.getenv('GITHUB_TOKEN')  # Use your GitHub Personal Access Token
    repo_name = os.getenv('GITHUB_REPO_NAME')
    username = os.getenv('GITHUB_USERNAME')
    
    g = Github(token)
    user = g.get_user()

    try:
        repo = user.get_repo(repo_name)
    except Exception as e:
        print(f"Error accessing repository {repo_name}: {e}")
        raise
    
    # Construct the path where the image will be uploaded
    path = f"{folder}/{file_name}"

    # Check if the file already exists in the repository
    try:
        contents = repo.get_contents(path)
        sha = contents.sha  # File exists, get the current SHA
        print(f"File {path} already exists, updating it.")
    except Exception as e:
        # File doesn't exist, proceed with creating a new file
        sha = None
        print(f"File {path} does not exist, creating a new one.")

    # Read the image as binary
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    # Create or update the file in the repository
    if sha:
        repo.update_file(path, "update match image", content, sha, branch="main")
    else:
        repo.create_file(path, "upload match image", content, branch="main")
    
    print(f"Image uploaded to GitHub at {path}")

    # Construct and return the raw URL of the uploaded image
    image_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{path}"
    
    # Validate the image URL by checking its content type
    response = requests.get(image_url)
    print(f"Image URL content type: {response.headers['Content-Type']}")
    if "image" not in response.headers['Content-Type']:
        raise Exception(f"Invalid content type for image: {response.headers['Content-Type']}")

    return image_url



# Function to send the video script to Synthesia and generate the video
def send_to_synthesia(video_script, home_team_name, away_team_name, background_image_url):
    url = "https://api.synthesia.io/v2/videos"
    
    avatar_id = "8f145381-e0d4-48e8-9a08-963430d58a5c"
    video_title = f"Prediction tip for {home_team_name} vs {away_team_name}"
    
    payload = {
        "test": True,
        "title": video_title,
        "description": video_script,
        "visibility": "public",
        "input": [
            {
                "scriptText": video_script,
                "avatar": avatar_id,
                "background": background_image_url
            }
        ],
        "aspectRatio": "16:9"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "016c0c7b5103c404a5569f109ebf569e"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            video_data = response.json()
            logging.info(f"Synthesia video created: {video_data}")
            print(f"Synthesia video created: {video_data}")
            return video_data['id']
        else:
            logging.error(f"Error creating Synthesia video. Status code: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in Synthesia video creation: {e}")
        return None

# Main function to execute the script
def main():
    match_data = fetch_odds_rank_and_last_5_games()

    home_team = match_data['home_team']
    away_team = match_data['away_team']

    image_path = generate_match_image(match_data, 1)

    folder = "images"
    file_name = os.path.basename(image_path)
    github_image_url = upload_image_to_github(image_path, folder, file_name)

    video_script = generate_video_script(match_data, match_data['prediction_result'], match_data['row_number'])

    print(f"Generated Video Script for {home_team} vs {away_team}:\n{video_script}")

    # video_url = send_to_synthesia(video_script, home_team, away_team, github_image_url)

    # if video_url:
    #     print(f"Video for {home_team} vs {away_team} is ready: {video_url}")
    # else:
    #     print(f"Error generating video for {home_team} vs {away_team}.")

if __name__ == "__main__":
    main()
