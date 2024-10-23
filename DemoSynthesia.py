import os
import requests
import logging
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from AIAvatarAPI import calculate_points, calculate_points_summary, calculate_rank_difference, classify_a_points, classify_a_team, classify_b_points, classify_b_team, generate_result, generate_video_script

# Function to fetch odds, rank, and last 5 games for both teams
def fetch_odds_rank_and_last_5_games():
    # Fetch data from the Predipie API
    url = "https://dataprovider.predipie.com/api/v1/ai/test/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")

    # Parse the JSON response
    data = response.json()
    match_data_list = []  # List to store match data

    for i, match in enumerate(data):
        # Extract match and team data
        match_id = match['id']
        home_team_name = match['home']['name']
        away_team_name = match['away']['name']
        home_odds = match['odds']['home']
        away_odds = match['odds']['away']
        league = match['competition']['name']
        start_time_str = match['start_time']
        stadium = match['venue']['name'] if match.get('venue') and match['venue'].get('name') else 'Unknown Stadium'

        # Convert match start time
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
        day = start_time.strftime("%A")
        time = start_time.strftime("%H:%M")

        # Determine team A (the team with lower odds) and team B
        if home_odds < away_odds:
            a_team_name = home_team_name
            b_team_name = away_team_name
            a_odds = home_odds
            b_odds = away_odds
        else:
            a_team_name = away_team_name
            b_team_name = home_team_name
            a_odds = away_odds
            b_odds = home_odds

        # Last 5 games for both teams
        team_a_last_5_games = match['team_related_match'][0]['five_previous_matches']
        team_b_last_5_games = match['team_related_match'][1]['five_previous_matches']
        a_wins, a_draws, a_losses = calculate_points_summary(team_a_last_5_games)
        b_wins, b_draws, b_losses = calculate_points_summary(team_b_last_5_games)

        # Rankings of the teams
        team_a_rank = match['team_related_match'][0]['rank']
        team_b_rank = match['team_related_match'][1]['rank']

        # Calculate points and classify groups
        a_points = calculate_points(team_a_last_5_games)
        b_points = calculate_points(team_b_last_5_games)
        a_recent_group = classify_a_points(a_points)
        b_recent_group = classify_b_points(b_points)
        rank_diff = calculate_rank_difference(team_a_rank, team_b_rank)

        # Classify teams based on odds
        a_team = classify_a_team(a_odds)
        b_team = classify_b_team(b_odds)

        # Generate the prediction result based on the data
        prediction_result, row_number = generate_result(a_team, b_team, a_recent_group, b_recent_group, rank_diff)

        # Prepare game data for generating content
        game_data = {
            'match_id': match_id,
            'home_team': home_team_name,
            'away_team': away_team_name,
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

        # Return the first match data (since you only want to process one match)
        return game_data


# Function to generate match image
def generate_match_image(match_data, match_number):
    # Load the template image
    img = Image.open("./assets/match-template.png")
    draw = ImageDraw.Draw(img)

    # Define font and size (adjusted for readability)
    font_path = "arial.ttf"
    font_team = ImageFont.truetype(font_path, 32)  # Adjust font size
    font_league = ImageFont.truetype(font_path, 30)
    font_details = ImageFont.truetype(font_path, 32)

    # Extract data for the match
    home_team_name = match_data['home_team']
    away_team_name = match_data['away_team']
    league = match_data['league']
    stadium = match_data['stadium']
    day = match_data['day']
    time = match_data['time']

    # Position and place the text
    draw.text((320, 615), home_team_name, fill="white", font=font_team)  # Home team
    draw.text((img.width - 630, 615), away_team_name, fill="white", font=font_team)  # Away team
    draw.text((img.width - 1140, 425), league, fill="white", font=font_league)  # League
    draw.text((img.width - 1140, 845), f"{day} {time}", fill="white", font=font_details)  # Date and time
    draw.text((img.width - 1140, 950), stadium, fill="white", font=font_details)  # Stadium

    # Save the image
    output_path = f"output_{home_team_name}_vs_{away_team_name}.png"
    img.save(output_path)
    print(f"Generated image for match {match_number} at {output_path}")
    return output_path  # Return the image path to be used in Synthesia


# Function to send the video script to Synthesia and generate the video
# Function to send the video script to Synthesia and generate the video
def send_to_synthesia(video_script, home_team_name, away_team_name, background_image_path):
    # Synthesia API URL to create video from template
    url = "https://api.synthesia.io/v2/videos/fromTemplate"
    
    # Replace with your actual template ID
    template_id = "edb119a1-5b62-4cbb-b064-22e9193de59e"  # Make sure this is correct
    
    # Ensure the template data matches what your Synthesia template expects
    payload = {
        "test": False,
        "templateId": template_id,
        "templateData": {
            "variable_1": "home_team_name",
            "variable_2": "away_team_name",
            "prediction_script": "Now, lets talk about the upcoming clash featuring Galatasaray. Looking at the bookmakers' data, Galatasaray steps onto the pitch with eye-catching odds of 1.25. For those not in the loop, these odds suggest a significant advantage over their opponents. This isnt just a small edge; its a cliff!",
            "background_image": background_image_path
        },
        "title": "Prediction tip for " + {home_team_name} + "vs" + {away_team_name},
        "description": "Now, lets talk about the upcoming clash featuring Galatasaray. Looking at the bookmakers' data, Galatasaray steps onto the pitch with eye-catching odds of 1.25. For those not in the loop, these odds suggest a significant advantage over their opponents. This isnt just a small edge; its a cliff!",
        "visibility": "private",
        "callbackId": "string"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "016c0c7b5103c404a5569f109ebf569e"
    }
    
    # Add logging for the raw response
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")  # Add this to inspect the response content

        if response.status_code == 201:
            video_data = response.json()
            logging.info(f"Synthesia video created: {video_data}")
            print(f"Synthesia video created: {video_data}")
            return video_data['id']
        else:
            logging.error(f"Error creating Synthesia video. Status code: {response.status_code}, Response: {response.text}")
            print(f"Error creating Synthesia video. Status code: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in Synthesia video creation: {e}")
        print(f"Error in Synthesia video creation: {e}")
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
    video_url = send_to_synthesia(video_script, home_team, away_team, background_image_path)

    if video_url:
        logging.info(f"Video ready: {video_url}")
        print(f"Video for {home_team} vs {away_team} is ready: {video_url}")
    else:
        logging.error(f"Error generating video for {home_team} vs {away_team}.")


if __name__ == "__main__":
    main()
