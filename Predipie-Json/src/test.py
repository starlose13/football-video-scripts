import requests
import sys
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import openai
import logging


SCOPES = ['https://www.googleapis.com/auth/drive.file']
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


if not openai.api_key:
    raise ValueError("API key not found! Set it in the .env file")

output_folder = "scene6"

def ensure_output_folder():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


# Define punctuation pause times
adjusted_reading_speed = 3.10

# Define punctuation pause times
pause_times = {
    ',': 0.21,
    '.': 0.21,
    '!': 0.18,
    '?': 0.18,
    ';': 0.17,
}



class AStatus:
    A1 = 0
    A2 = 1
    A3 = 2
    A4 = 3
    A5 = 4
    A6 = 5
    A7 = 6

class BStatus:
    B1 = 0
    B2 = 1
    B3 = 2
    B4 = 3
    B5 = 4
    B6 = 5
    B7 = 6

class RankDifference:
    bigDifference = 0
    mediumDifference = 1
    smallDifference = 2



# Logging setup for debugging
logging.basicConfig(level=logging.INFO)

# Function to fetch odds, rank, and last 5 games for both teams
def fetch_odds_rank_and_last_5_games():
    # Fetch data from the Predipie API
    url = "https://dataprovider.predipie.com/api/v1/ai/test/"
    response = requests.get(url)
    # verify=certifi.where()
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

        # Generate match result and card using OpenAI, and capture the prompt used
        prompt_text, card_choice = generate_match_result_with_openai(
            a_team_name, b_team_name, home_team_name, away_team_name, prediction_result
        )

        # Calculate word count and punctuation pause time
        word_count = len(prompt_text.split())
        pause_time = sum(prompt_text.count(p) * pause_times.get(p, 0) for p in pause_times)

        # Calculate reading time
        reading_time = round((word_count / adjusted_reading_speed) + pause_time, 2)

        # Prepare game data for JSON output
        game_data_json = {
            "description": prompt_text,
            "word_count": word_count,
            "reading_time": reading_time,
            "team_home": home_team_name,
            "team_away": away_team_name,
            "card": card_choice
        }



        match_data_list.append({
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
        })


        # Save the structured JSON data to a file
        output_path = os.path.join(output_folder, f"match_{i+1}.json")
        with open(output_path, 'w') as file:
            json.dump(game_data_json, file, indent=4)

        print(f"Saved results for match {match_id} in {output_path}")
        print("=" * 50)

    print("All games processed successfully.")
    return match_data_list


def generate_match_result_with_openai(a_team_name, b_team_name, home_team_name, away_team_name, prediction_result):
    """Generates a match result description, card, and returns the prompt text used based on the prediction."""

    # Define condition text and card based on the prediction result condition
    if prediction_result == "A win or draw":
        if a_team_name == home_team_name:
            condition_text = f"My AI analysis suggests {a_team_name} will win or draw, so the card should be 'Win or Draw Home Team'."
            card = "Win or Draw Home Team"
        elif a_team_name == away_team_name:
            condition_text = f"My AI analysis suggests {a_team_name} will win or draw, so the card should be 'Win or Draw Away Team'."
            card = "Win or Draw Away Team"
        else:
            condition_text = "My AI analysis suggests an uncertain outcome."
            card = "none"
    elif prediction_result == "A or B win":
        condition_text = f"My AI analysis suggests either {a_team_name} or {b_team_name} will win, so the card should be 'Win Home or Away Team'."
        card = "Win Home or Away Team"
    elif prediction_result == "A win":
        if a_team_name == home_team_name:
            condition_text = f"My AI analysis suggests {a_team_name} will win, so the card should be 'Win Home Team'."
            card = "Win Home Team"
        elif a_team_name == away_team_name:
            condition_text = f"My AI analysis suggests {a_team_name} will win, so the card should be 'Win Away Team'."
            card = "Win Away Team"
        else:
            condition_text = "My AI analysis suggests an uncertain outcome."
            card = "none"
    else:
        condition_text = "No specific result is found for this prediction."
        card = "none"

    # Build the complete prompt
    prompt = (
    f"{condition_text}. Write this dynamically for football fans, keeping it very brief—under 25 words! "
    f"Use these punctuation marks frequently in the output: dot, comma, exclamation mark, question mark, and semicolon. "
    f"Important: Avoid words like 'bet,' 'betting,' or 'place bet,' do not use apostrophes, em dashes, or similar punctuation marks."
)



    # Use OpenAI API to generate the result summary and card
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant generating football match result summaries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )

    # Extract generated result description from the response
    generated_script = response['choices'][0]['message']['content'].strip()

    # Return the prompt text, generated description, and card
    return generated_script, card



# Helper function to calculate wins, draws, and losses
def calculate_points_summary(last_5_games):
    if not isinstance(last_5_games, list):
        logging.error("Invalid input: last_5_games should be a list")
        return 0, 0, 0  # Default to 0 wins, draws, and losses if input is invalid

    valid_results = {'w', 'd', 'l'}
    wins, draws, losses = 0, 0, 0

    # Ensure we only count valid game results ('w', 'd', 'l')
    for result in last_5_games:
        if result == 'w':
            wins += 1
        else:
            logging.warning(f"Unexpected game result: {result}, ignoring it.")

    logging.info(f"Summary: {wins} wins, {draws} draws, {losses} losses")
    return wins, draws, losses



# Function to calculate points based on last 5 games
def calculate_points(last_5_games):
    if not isinstance(last_5_games, list):
        logging.error("Invalid input: last_5_games should be a list")
        return 0  # Return 0 points if the input is invalid

    points = 0

    for game in last_5_games:
        if game == 'w':  # Win
            points += 3
        elif game == 'd':  # Draw
            points += 1
        elif game != 'l':  # Loss doesn't add points, but handle unexpected values
            logging.warning(f"Unexpected game result: {game}, ignoring it.")

    logging.info(f"Total points calculated: {points}")
    return points

def classify_a_points(a_points):
    if not isinstance(a_points, (int, float)) or a_points < 0:
        logging.error(f"Invalid points: {a_points}. Points must be a non-negative number.")
        return "Unknown Group"
    if 13 <= a_points <= 15:
        group = "ARecentG1"
    else:
        group = "ARecentG7"

    logging.info(f"Classified {a_points} points into group: {group}")
    return group

def classify_b_points(b_points):
    if not isinstance(b_points, (int, float)) or b_points < 0:
        logging.error(f"Invalid points: {b_points}. Points must be a non-negative number.")
        return "Unknown Group"
    if 13 <= b_points <= 15:
        group = "BRecentG1"
    else:
        group = "BRecentG7"

    logging.info(f"Classified {b_points} points into group: {group}")
    return group


def calculate_rank_difference(rank_a, rank_b):
    # Validate inputs
    if not isinstance(rank_a, int) or not isinstance(rank_b, int):
        logging.error(f"Invalid rank inputs: rank_a={rank_a}, rank_b={rank_b}. Both ranks should be integers.")
        return None
    
    if rank_a < 0 or rank_b < 0:
        logging.error(f"Invalid ranks: rank_a={rank_a}, rank_b={rank_b}. Ranks should be non-negative.")
        return None
    
    # Calculate rank difference
    rank_diff = abs(rank_a - rank_b)
    
    # Classify the rank difference
    if rank_diff > 8:
        classification = RankDifference.bigDifference
    else:
        classification = RankDifference.smallDifference

    # Log the classification result
    logging.info(f"Rank difference between rank_a={rank_a} and rank_b={rank_b} is classified as: {classification}")
    return classification

def classify_a_team(a_odds):
    # Validate input
    if not isinstance(a_odds, (int, float)) or a_odds < 0:
        logging.error(f"Invalid odds: {a_odds}. Odds must be a non-negative number.")
        return "Unknown Classification"

    # Classify based on odds ranges
    if a_odds <= 1.30:
        classification = "A1"
    elif 1.31 <= a_odds <= 1.50:
        classification = "A2"
    else:
        classification = "A7"

    # Log the classification result
    logging.info(f"Odds {a_odds} classified as: {classification}")
    return classification


def classify_b_team(b_odds):
    # Validate input
    if not isinstance(b_odds, (int, float)) or b_odds < 0:
        logging.error(f"Invalid odds: {b_odds}. Odds must be a non-negative number.")
        return "Unknown Classification"

    if b_odds <= 1.30:
        classification = "B1"
    else:
        classification = "B7"

    # Log the classification result
    logging.info(f"Odds {b_odds} classified as: {classification}")
    return classification


def generate_result(a_team, b_team, a_recent_g, b_recent_g, rank_diff):

    if a_team == "A1":
        return "A win", 1
    elif a_team == "A2" and a_recent_g == "ARecentG1":
        return "A win", 2

    elif a_team == "A7" and b_team == "B7":
        return "Special Case", 67
    logging.warning(f"No result found for the combination: {a_team}, {b_team}, {a_recent_g}, {b_recent_g}, {rank_diff}")
    return "No result found", None

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    # Fetch the match data
    ensure_output_folder()
    match_data_list = fetch_odds_rank_and_last_5_games()


if __name__ == "__main__":
    main()

