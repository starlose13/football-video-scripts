import requests
import sys
import re
from dotenv import load_dotenv
import os
from datetime import datetime
import random
import openai
from end_messages import end_messages
import logging
from github import Github
import base64
import certifi
import time

SCOPES = ['https://www.googleapis.com/auth/drive.file']
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
creatify_api_id = os.getenv('CREATIFY_API_ID')
creatify_api_key = os.getenv('CREATIFY_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_API_URL = "https://api.github.com"

if not openai.api_key:
    raise ValueError("API key not found! Set it in the .env file")
if not creatify_api_id or not creatify_api_key:
    raise ValueError("Creatify API credentials not found! Set them in the .env file")

# Enums for status and recent game groups

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

class EndMessageManager:
    def __init__(self):
        self.end_messages = end_messages

    # Shuffle messages
    def shuffle_messages(self):
        random.shuffle(self.end_messages)
    
    # Retrieve a random message
    def get_random_message(self):
        return random.choice(self.end_messages)


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

        # Prepare game data for generating content
       
        game_data = {
            'match_id' : match_id,
            'home_team': home_team_name,
            'away_team': away_team_name,
            'a_team_name': a_team_name, 'b_team_name': b_team_name,
            'a_team_odds': a_odds,'b_team_odds': b_odds,
            'team_a_last_5': team_a_last_5_games,'team_b_last_5': team_b_last_5_games,
            'team_a_rank': team_a_rank,'team_b_rank': team_b_rank,
            'a_wins': a_wins, 'a_draws': a_draws, 'a_losses': a_losses,
            'b_wins': b_wins, 'b_draws': b_draws, 'b_losses': b_losses,
            'league': league,
            'stadium': stadium,
            'day': day,
            'time': time
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
        video_script = generate_video_script(game_data, prediction_result,row_number)

        print(f"Generated Video Script for {home_team_name} vs {away_team_name}:\n", video_script)
        if prediction_result == "A win or draw":
            print(f"Match {match_id}: {a_team_name} win or draw (Row {row_number})")
        elif prediction_result == "A or B win":
            print(f"Match {match_id}: {a_team_name} or {b_team_name} win (Row {row_number})")
        elif prediction_result == "A win":
            print(f"Match {match_id}: {a_team_name} win (Row {row_number})")
        else:
            print(f"Match {match_id}: No result found (Row {row_number})")
        print(f"{'='*50}\n")
        print("=" * 50)

    print("All games processed successfully.")
    return match_data_list


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
        elif result == 'd':
            draws += 1
        elif result == 'l':
            losses += 1
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
    valid_results = {'w', 'd', 'l'}

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
    elif 11 <= a_points <= 12:
        group = "ARecentG2"
    elif 9 <= a_points <= 10:
        group = "ARecentG3"
    elif 7 <= a_points <= 8:
        group = "ARecentG4"
    elif 5 <= a_points <= 6:
        group = "ARecentG5"
    elif 3 <= a_points <= 4:
        group = "ARecentG6"
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
    elif 11 <= b_points <= 12:
        group = "BRecentG2"
    elif 9 <= b_points <= 10:
        group = "BRecentG3"
    elif 7 <= b_points <= 8:
        group = "BRecentG4"
    elif 5 <= b_points <= 6:
        group = "BRecentG5"
    elif 3 <= b_points <= 4:
        group = "BRecentG6"
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
    elif 4 <= rank_diff <= 7:
        classification = RankDifference.mediumDifference
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
    elif 1.51 <= a_odds <= 1.80:
        classification = "A3"
    elif 1.81 <= a_odds <= 2.00:
        classification = "A4"
    elif 2.01 <= a_odds <= 2.30:
        classification = "A5"
    elif 2.31 <= a_odds <= 2.80:
        classification = "A6"
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

    # Classify based on odds ranges
    if b_odds <= 1.30:
        classification = "B1"
    elif 1.31 <= b_odds <= 1.50:
        classification = "B2"
    elif 1.51 <= b_odds <= 1.80:
        classification = "B3"
    elif 1.81 <= b_odds <= 2.00:
        classification = "B4"
    elif 2.01 <= b_odds <= 2.30:
        classification = "B5"
    elif 2.31 <= b_odds <= 2.80:
        classification = "B6"
    else:
        classification = "B7"

    # Log the classification result
    logging.info(f"Odds {b_odds} classified as: {classification}")
    return classification


def generate_result(a_team, b_team, a_recent_g, b_recent_g, rank_diff):

    # Rows 1-17 (A2 as A team)
    if a_team == "A1":
        return "A win", 1
    elif a_team == "A2" and a_recent_g == "ARecentG1":
        return "A win", 2
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG7":
        return "A win", 3
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG6":
        return "A win", 4
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG5":
        return "A win", 5
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4":
        return "A win", 6
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG3":
        return "A win or draw", 7
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2":
        return "A win or draw", 8
    elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1":
        return "A win or draw", 9
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG7":
        return "A win", 10
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG6":
        return "A win", 11
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5":
        return "A win", 12
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG4":
        return "A win or draw", 13
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG3":
        return "A win or draw", 14
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG2":
        return "A win or draw", 15
    elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG1":
        return "A win or draw", 16
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7":
        return "A win", 17

    # Rows 18-26 (Rank differences)
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "bigDifference":
        return "A win", 18
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "mediumDifference":
        return "A win", 19
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "smallDifference":
        return "A win or draw", 20
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5":
        return "A win or draw", 21
    elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
        return "A win or draw", 22
    elif a_team == "A2" and a_recent_g == "ARecentG5":
        return "A win or draw", 23
    elif a_team == "A2" and a_recent_g == "ARecentG6":
        return "A win or draw", 24
    elif a_team == "A2" and a_recent_g == "ARecentG7":
        return "A win or draw", 25
    elif a_team == "A3":
        return "A win or draw", 26  # Corrected to "A win or draw"
    elif a_team == "A4":
        return "A win or draw", 27

    # Rows 28-36 (A5 as A team)
    elif a_team == "A5" and b_team == "B7":
        return "A win or draw", 28
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG1":
        return "A win or draw", 29
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG2":
        return "A win or draw", 30
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG3":
        return "A win or draw", 31
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7":
        return "A win or draw", 32
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6":
        return "A win or draw", 33
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5":
        return "A win or draw", 34
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
        return "A win or draw", 35
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
        return "A or B win", 36
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
        return "A or B win", 37

    # Rows 38-44 (A5 and A6 with B7)
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG5":
        return "A or B win", 38
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG6":
        return "A or B win", 39
    elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG7":
        return "A or B win", 40
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
        return "A win or draw", 41
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
        return "A win or draw", 42
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
        return "A win or draw", 43
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4":
        return "A win or draw", 44

    # Rows 45-57 (Rank differences and A7 as A team)
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
        return "A win or draw", 45
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
        return "A or B win", 46
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
        return "A or B win", 47
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG2":
        return "A or B win", 48
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG3":
        return "A or B win", 49
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG4":
        return "A or B win", 50
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG5":
        return "A win or draw", 51  # Corrected to "A win or B win"
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG6":
        return "A win or draw", 52
    elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG7":
        return "A win or draw", 53
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
        return "A win or draw", 54
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
        return "A win or draw", 55
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
        return "A win or draw", 56
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4":
        return "A win or draw", 57

    # Rows 58-66 (Remaining A7 conditions)
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
        return "A win or draw", 58
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
        return "A or B win", 59
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference":
        return "A win or draw", 60
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
        return "A win or draw", 61
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
        return "A or B win", 62
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2":
        return "A or B win", 63
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG1":
        return "A or B win", 64
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1":
        return "A or B win", 65
    elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2":
        return "A or B win", 66

    # Row 67 (Special case)
    elif a_team == "A7" and b_team == "B7":
        return "Special Case", 67
    logging.warning(f"No result found for the combination: {a_team}, {b_team}, {a_recent_g}, {b_recent_g}, {rank_diff}")
    # Default condition if no match is found
    return "No result found", None



def generate_long_form_output(row_number, team_a_name, team_b_name, a_odds_variable,b_odds_variable, a_wins, a_draws, a_losses, b_wins , b_draws , b_losses , team_a_rank , team_b_rank ):
    if row_number == 1:
        return f"Coefficients are considered the main and most accurate factor in approaching the correct prediction. The coefficient of {a_odds_variable} is proof of the big difference between the two teams, which makes us unnecessary to analyze other factors involved in this game. We suggest you choose board {team_a_name} and watch the game in peace."
    
    elif row_number == 2:
        return f"Given that {team_a_name} Team has recorded {a_wins} wins, {a_draws} draws, and {a_losses} losses in their last five matches, combined with the current winning odds of {a_odds_variable}, it’s highly likely that they will secure another victory. The most probable outcome for this game is a win for {team_a_name} Team."
    
    elif row_number in [3, 4, 5]:
        return f"Based on Team {team_a_name}’s recent form, having achieved {a_wins} wins, {a_draws} draws, and {a_losses} losses, it is clear they are well-positioned for another victory in this match. Furthermore, the poor performance of  {team_b_name} Team further strengthens our confidence in Team {team_a_name}'s success. With favorable odds of {a_odds_variable},{team_a_name} Team win seems more certain as the match approaches."
    
    elif row_number == 6:
        return f"{team_b_name} Team appears to be a tenacious opponent, showing resilience in their last few games. However, their results of {b_wins} wins, {b_draws} draws, and {b_losses} losses, combined with the reliable odds of {b_odds_variable} for {team_a_name} Team , make it hard to envision any result other than a win for {team_a_name} Team."
    
    elif row_number in [7, 8, 9]:
        return f"Both teams have shown decent form in recent matches, especially {team_a_name} Team , who has the additional advantage of favorable odds at {a_odds_variable}. While Team {team_a_name} Team seems the likely winner, for added assurance, selecting the 'win or draw' option for Team {team_a_name} would be a safe bet."
    
    elif row_number in [10, 11, 12]:
        return f"Along with the low odds of {a_odds_variable} and the results from Team {team_b_name}’s recent performances — including {b_wins} wins, {b_draws} draws, and {b_losses} losses — we are inclined to choose {team_a_name} Team as the winner. Predipie suggestion is to back {team_a_name} Team with confidence."
    
    elif row_number in [13, 14, 15]:
        return f"While the solid odds of {a_odds_variable} favor Team {team_a_name}, we cannot completely rule out {team_b_name} Team, who, despite their slim chances on paper, have shown some potential in past games. Given their record of {b_wins} wins, {b_draws} draws, and {b_losses} losses, it might be wiser to select a 'win or draw' for {team_a_name} Team to ensure a more accurate prediction."
    
    elif row_number == 17:
        return f"{team_a_name} Team less-than-stellar recent form can be overlooked when compared to Team {team_b_name}’s very poor results. Therefore, the key factor in our decision is the odds of {a_odds_variable}, making it advisable to back {team_a_name} Team with minimal risk and watch the game, hoping for their victory."
    
    elif row_number in [18, 19]:
        return f"The unremarkable recent form of both teams makes it difficult to analyze their past games. Despite this, we recommend trusting the reliable odds of {a_odds_variable} and the points difference between them in the standings — with {team_a_name} Team ranked at {team_a_rank} and {team_b_name} Team at {team_b_rank} — to back {team_a_name} Team as the clear winner."
    
    elif row_number == 20:
        return f" {team_a_name} Team’s recent performance of {a_wins} wins, {a_draws} draws, and {a_losses} losses, combined with the narrow points gap between the two teams in the standings, makes it hard to confidently predict a Team {team_a_name} victory. However, with the favorable odds of {a_odds_variable}, the best option would be a 'win or draw' for {team_a_name} Team."
    
    elif row_number in [21, 22]:
        return f"Both {team_a_name} Team and {team_b_name} Team have had similar results in their last five matches. In such cases, the only trustworthy factor is the odds. We suggest selecting a 'win or draw' for {team_a_name} Team to ease your mind since the odds of {a_odds_variable} for Team {team_a_name} don’t guarantee a straightforward win."
    
    elif row_number in [23, 24, 25]:
        return f"The weak recent performance of Team {team_a_name} and their last five-game record shows that the odds of {a_odds_variable} for {team_a_name} Team may not be entirely reliable. Therefore, we recommend backing {team_a_name} Team with a 'win or draw' option for added certainty."
    
    elif row_number in [26, 27]:
        return f"The odds of {a_odds_variable} for {team_a_name} Team and {b_wins} for {team_b_name} Team make it unlikely that {team_b_name} Team can secure a win against {team_a_name} Team. However, they still present a tough challenge, so the best choice would be a 'win or draw' for Team {team_a_name}."
    
    elif row_number in [28, 29, 30, 31]:
        return f"As the odds between the two teams become closer, predicting a winner depends on other factors, particularly recent performances. With {team_a_name} Team’s strong record and better odds, it seems unlikely that they will lose.'win or draw' for {team_a_name} Team appears to be the most probable outcome."
    
    elif row_number in [32, 33, 34]:
        return f"Based on recent results, {team_a_name} Team with {a_wins} wins, {a_draws} draws, and {a_losses} losses, is in a better position than {team_b_name} Team, who has recorded {b_wins} wins, {b_draws} draws, and {b_losses} losses. The odds for {team_a_name} Team at {a_odds_variable} and for {team_b_name} Team further tilt the balance toward {team_a_name} Team, making a 'win or draw' prediction for {team_a_name} Team is a smart choice."
    
    elif row_number == 35:
        return f"Everything in this game seems to be close — the odds slightly favor {team_a_name} Team, but both teams have had similar results in recent matches. However, the points difference between them in the standings — with {team_a_name} Team at {team_a_rank} and {team_b_name} Team at {team_b_rank} — makes Team {team_a_name} the more favorable option. We suggest going with a 'win or draw' for {team_a_name} Team to make the most likely prediction."
    
    # Row 36-37
    if row_number in [36, 37]:
        return f"The relatively similar odds and recent form of both teams suggest that this will be a closely contested match. With only a small difference in their standings, it looks like either team could win. It’s best to opt for the 'double chance' card, eliminating the draw as an option. win of {team_a_name} or {team_b_name} without drawing."

    # Row 38-40
    elif row_number in [38, 39, 40]:
        return f"As you can see, the odds {a_odds_variable} for {team_a_name} Team slightly tip the balance in their favor. However, their poor results in recent matches make it difficult to rule out {team_b_name} Team's chances of winning. With a bit of luck, either team’s victory seems like the most likely outcome for this game. win of {team_a_name} or {team_b_name} without drawing."

    # Row 41-43
    elif row_number in [41, 42, 43]:
        return f"When the odds are close, predicting the winner becomes much more challenging. The odds for {team_a_name} Team at {a_odds_variable} and for {team_b_name} Team don't provide much insight into the final result. However, with {team_a_name} Team’s strong recent record of {a_wins} wins, {a_draws} draws, and {a_losses} losses, they seem to be well-prepared for this match. On the other hand, {team_b_name} Team’s record of {b_wins} wins, {b_draws} draws, and {b_losses} losses suggests that using the 'win or draw' card for {team_a_name} Team is a solid choice."

    # Row 44-45
    elif row_number in [44, 45]:
        return f"The odds for {team_a_name} Team at {a_odds_variable} and for {team_b_name} Team suggest that more information is needed to predict this match accurately.{team_a_name} Team’s excellent record of {a_wins} wins, {a_draws} draws, and {a_losses} losses makes a defeat for them seem unlikely. Although {team_b_name} Team has also managed to achieve {b_wins} wins, {b_draws} draws, and {b_losses} losses, the best choice is still the 'win or draw' card for {team_a_name} Team."

    # Row 46-47
    elif row_number in [46, 47]:
        return f"The numbers indicate that this will be a very close match, with odds of {a_odds_variable} for {team_a_name} Team and for {team_b_name} Team. This makes it difficult to make a straightforward decision. Furthermore, when we look at the last five matches for both teams, we see that they are coming into this game with good results. With {team_a_name} Team’s record of {a_wins} wins, {a_draws} draws, and {a_losses} losses, and {team_b_name} Team’s record of {b_wins} wins, {b_draws} draws, and {b_losses} losses, a victory for either team seems more likely than a draw. We recommend using the 'double chance' card, excluding the draw."

    # Row 48-50
    elif row_number in [48, 49, 50]:
        return f" {team_a_name} Team , with odds of {a_odds_variable}, is in a better position than {team_b_name} Team, whose winning odds are at. However,{team_a_name} Team’s last five games have been unimpressive, with a record of {a_wins} wins, {a_draws} draws, and {a_losses} losses. Therefore, to make the safest prediction, we recommend using the 'win or draw' card for {team_a_name} Team."

    # Row 51-53
    elif row_number in [51, 52, 53]:
        return f"Sometimes, the meaning of the odds can change based on a team's recent performances. {team_a_name} Team recent results make it hard to rely solely on their odds of {a_odds_variable}. For this match, it's best to consider the possibility of either team winning and use the 'double chance' card, excluding the draw."

    # Row 54-56
    elif row_number in [54, 55, 56]:
        return f"It’s hard to say which team will emerge victorious here, as the odds of {a_odds_variable} for {team_a_name} Team and for {team_b_name} Team are very close. However, with {team_a_name} Team strong record over the last five matches, we feel confident in recommending the 'win or draw' card for {team_a_name} Team, which seems to be the most likely outcome."

    # Row 57-58
    elif row_number in [57, 58]:
        return f"When both teams have high odds like {a_odds_variable} for {team_a_name} Team and for {team_b_name} Team, it’s necessary to look at their recent results. {team_a_name} Team has performed better in their last five games, so we recommend using the 'win or draw' card for {team_a_name} Team and watching the match with confidence."

    # Row 59
    elif row_number == 59:
        return f"It's extremely difficult to determine the winner when both teams have similar form. In these kinds of games, both teams have almost equal chances of winning. Home advantage may play a role, but our suggestion is to back either team for the win and to exclude the draw from your prediction."

    # Row 60-61
    elif row_number in [60, 61]:
        return f"When the odds are as close as they are for this game, they don’t offer much help. {team_a_name} Team record of {a_wins} wins, {a_draws} draws, and {a_losses} losses, and {team_b_name} Team’s record of {b_wins} wins, {b_draws} draws, and {b_losses} losses give us better insights. {team_a_name} Team’s positive form suggests it’s safer to go with the 'win or draw' card for {team_a_name} Team and make a well-calculated risk."

    # Row 62
    elif row_number == 62:
        return f" {team_a_name} Team’s recent performance of {a_wins} wins, {a_draws} draws, and {a_losses} losses makes them seem more prepared than {team_b_name} Team. Although {team_b_name} Team has also achieved a decent result of {b_wins} wins, {b_draws} draws, and {b_losses} losses, the small gap in their standings is worth noting. {team_a_name} Team is in position {team_a_rank} on the table, while {team_b_name} Team is in position {team_b_rank}, making the 'double chance' card the safest bet. win of {team_a_name} or {team_b_name} without drawing."

    # Row 63-66
    elif row_number in [63, 64, 65, 66]:
        return f"It’s hard to pinpoint the winner of this game. The stats and odds for both teams are almost equal, and their performances against previous opponents are also very similar. With {team_a_name} Team’s record of {a_wins} wins, {a_draws} draws, and {a_losses} losses, and {team_b_name} Team’s record of {b_wins} wins, {b_draws} draws, and {b_losses} losses, this match will be a tough one to predict. In the end, backing either team to win may be the safest choice to navigate this difficult game."
    elif row_number in [67]:
        return f"The equal coefficients of the two teams indicate a very close game, when we visit the recent games of the two teams, we see that {a_wins} victory {a_draws} draw {a_losses} defeat was recorded for team {team_a_name} and {b_wins} victory {b_draws} draw {b_losses} defeat, the results of the team {team_b_name} is In such a situation, we suggest you to choose a `win or draw` for the home team, because the hosting score is a very important score if the two teams are not superior to each other."
    # Default message for unmatched rows
    else:
        return f"No detailed analysis available for row number {row_number}"


# Function to sanitize text (removes non-ASCII characters and unsupported symbols)
def sanitize_text(text):
    # Remove non-ASCII characters
    sanitized_text = text.encode('ascii', 'ignore').decode('ascii')

    # Optionally, remove or replace other problematic characters like "▒"
    sanitized_text = re.sub(r'[^\x00-\x7F]+', '', sanitized_text)

    # Strip leading/trailing spaces and return
    return sanitized_text.strip()

def generate_video_script(game_data, prediction_result, row_number):
    # Generate dynamic text based on the long-form output that reflects the prediction
    long_form_output = generate_long_form_output(row_number, game_data['a_team_name'], game_data['b_team_name'],game_data['a_team_odds'], game_data['b_team_odds'], game_data['a_wins'], game_data['a_draws'], game_data['a_losses'],game_data['b_wins'], game_data['b_draws'], game_data['b_losses'],game_data['team_a_rank'], game_data['team_b_rank'])
    
    # Create the prompt for OpenAI
    prompt = f"""

    """



    # You are an AI video script writer. I will provide you with information about football matches via API, including a prediction for each match. Use this data to create an engaging video script for predicting the outcome, and include a disclaimer.
    # Use the following data to write the script:
    # - Home team name: [Host_Team] = {game_data['a_team_name']}, 
    # - Away team name: [Guest_Team] = {game_data['b_team_name']},
    # - Game time: [Game_Time] = {game_data['time']},
    # - Game date: [Game_Date] = {game_data['day']},
    # - Home team odds: [Host_Odds] = {game_data['a_team_odds']},
    # - Away team odds: [Guest_Odds] = {game_data['b_team_odds']},
    # - Last 5 matches of the home team (wins, draws, losses): [Host_Recent_Results] :
    # {game_data['team_a_last_5']},
    # {game_data['a_wins']},
    # {game_data['a_draws']},
    # {game_data['a_losses']},
    # - Last 5 matches of the away team (wins, draws, losses): [Guest_Recent_Results]
    # {game_data['team_b_last_5']},
    # {game_data['b_wins']},
    # {game_data['b_draws']},
    # {game_data['b_losses']},
    # - Prediction for the game outcome: [Prediction] {prediction_result}

    # Structure the video script as follows:

    # 1. Start with an enthusiastic introduction, welcoming PrediPie fans and introducing the match prediction segment.
    # 2. Introduce the first match with team names, time, and date.
    # 3. Present the odds for each team and the draw.
    # 4. Analyze the recent performance of both the home and away teams over the last 5 matches.
    # 5. Conclude with an exciting prediction based on the API data, and include a disclaimer about the AI nature of the prediction.

    # Expected output example:
    # "Hello again to all PrediPie fans! As always, we’re back to analyze five games together and make some bold predictions.  
    # Our first match-up is between {game_data['a_team_name']} and {game_data['b_team_name']}, kicking off at  {game_data['time']} on {game_data['day']}.  
    # Here are the odds: home team {game_data['a_team_odds']}, away team {game_data['b_team_odds']}.  
    # The home team has shown {game_data['team_a_last_5']},{game_data['a_wins']},{game_data['a_draws']},{game_data['a_losses']} in their last 5 games, while the away team has recorded {game_data['team_b_last_5']},{game_data['b_wins']},{game_data['b_draws']},{game_data['b_losses']}.  
    # Now, what’s our prediction? Based on the data, my AI-based analysis suggests {prediction_result}. Keep in mind, I’m an AI making these predictions, so there’s always a chance I might be wrong, and this is not financial advice. Let’s enjoy the game and see how it unfolds!"

    # Please write a script following this structure.

    # Use OpenAI API to generate the video script
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to create dynamic football video scripts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400
    )
    generated_script = response['choices'][0]['message']['content'].strip()

    # Sanitize the generated text before using it
    sanitized_script = sanitize_text(generated_script)

    return sanitized_script
    # Extract and return the generated script


# Function to upload the video script to GitHub
def upload_file_to_github(repo_name, file_path, commit_message):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token not found in environment variables")
    
    # Authenticate using the token
    g = Github(token)
    
    # Get the repository object
    repo = g.get_user().get_repo(repo_name)
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define the file path in the repo (you can adjust this as needed)
    repo_file_path = f"video_scripts/{os.path.basename(file_path)}"
    
    try:
        # Check if the file already exists
        contents = repo.get_contents(repo_file_path)
        # If it exists, update the file
        repo.update_file(contents.path, commit_message, content, contents.sha)
        print(f"Updated {repo_file_path} in {repo_name}")
    except:
        # If it does not exist, create a new file
        repo.create_file(repo_file_path, commit_message, content)
        print(f"Created {repo_file_path} in {repo_name}")

    # Return the URL to the file on GitHub
    return f"https://raw.githubusercontent.com/{repo.owner.login}/{repo_name}/main/{repo_file_path}"


# Enable GitHub Pages for the repository
def enable_github_pages(repo_name):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        github_pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
        print(f"GitHub Pages enabled: {github_pages_url}")
        return github_pages_url
    else:
        print(f"Failed to enable GitHub Pages: {response.json()}")
        return None
# Function to queue AI Avatar lipsync task (simplified version)
def generate_ai_avatar_lipsync(script, creator="5021bec0-f33f-43e6-b0e3-1cb7f76003c6", aspect_ratio="1:1"):
    url = "https://api.creatify.ai/api/lipsyncs/"
    headers = {
        "X-API-ID": os.getenv("CREATIFY_API_ID"),
        "X-API-KEY": os.getenv("CREATIFY_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "text": script,  # The video script generated by OpenAI
        "creator": creator,
        "aspect_ratio": aspect_ratio,
        # Removed optional fields: no_caption, no_music, caption_style
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
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



# Function to check the status of the AI Avatar lipsync video (replaces check_preview_status and check_render_status)
def check_ai_avatar_status(lipsync_id):
    url = f"https://api.creatify.ai/api/lipsyncs/{lipsync_id}/"
    headers = {
        "X-API-ID": os.getenv("CREATIFY_API_ID"),
        "X-API-KEY": os.getenv("CREATIFY_API_KEY")
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
    

def send_to_ai_avatar(video_script):
    lipsync_id = generate_ai_avatar_lipsync(video_script)
    if lipsync_id:
        start_time = time.time()
        timeout = 1200  # Extend timeout to 20 minutes
        wait_time = 20  # Start with a 20-second interval
        max_wait_time = 60  # Maximum wait time between retries

        while True:
            lipsync_data = check_ai_avatar_status(lipsync_id)
            if lipsync_data:
                if lipsync_data['status'] == 'done':
                    logging.info(f"Lipsync video generated: {lipsync_data}")
                    return lipsync_data['output']  # Return the video URL
                elif lipsync_data['status'] == 'failed':
                    logging.error(f"Lipsync generation failed: {lipsync_data.get('failed_reason', 'Unknown reason')}")
                    return None  # Handle failure case
                elif lipsync_data['status'] == 'in_queue':
                    logging.info(f"Video is still in queue. Waiting for {wait_time} seconds before retrying.")
                    time.sleep(wait_time)
                    wait_time = min(wait_time * 2, max_wait_time)  # Exponential backoff
                else:
                    logging.warning(f"Unexpected status: {lipsync_data['status']}. Retrying...")
            else:
                logging.error("Failed to retrieve lipsync data.")
                return None

            if time.time() - start_time > timeout:
                logging.error("Lipsync video generation timeout.")
                return None  # Return early to avoid infinite wait

    else:
        logging.error("Error queuing AI Avatar video.")
        return None
    


# Main function to execute the script
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    # Fetch the match data
    match_data_list = fetch_odds_rank_and_last_5_games()

    for game_data in match_data_list:
        home_team = game_data['home_team']
        away_team = game_data['away_team']

        # Generate the video script using the precomputed prediction result and row number
        video_script = generate_video_script(game_data, game_data['prediction_result'], game_data['row_number'])

        # Log the generated script
        print(f"Generated Video Script for {home_team} vs {away_team}:\n", video_script)

        # Send the script to AI Avatar and generate a video
        # video_url = send_to_ai_avatar(video_script)

        # if video_url:
        #     logging.info(f"Video ready: {video_url}")
        #     print(f"Video for {home_team} vs {away_team} is ready: {video_url}")
        # else:
        #     logging.error(f"Error generating video for {home_team} vs {away_team}.")

    print("All matches processed successfully.")


if __name__ == "__main__":
    main()

