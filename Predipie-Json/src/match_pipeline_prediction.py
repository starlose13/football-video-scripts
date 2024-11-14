# scene6_pipeline.py

import os
import json
import logging
from data_processor import MatchDataProcessor 
import requests
from datetime import datetime
from dotenv import load_dotenv
import openai

# کد کامل شما اینجا قرار می‌گیرد
class MatchPredictionPipeline:
    def __init__(self, api_url, folder_name='scene6'):
        self.api_url = api_url
        self.output_folder = folder_name
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("API key not found! Set it in the .env file")

    def ensure_output_folder(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)


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
    def fetch_odds_rank_and_last_5_games(self):
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
            a_wins, a_draws, a_losses = self.calculate_points_summary(team_a_last_5_games)
            b_wins, b_draws, b_losses = self.calculate_points_summary(team_b_last_5_games)

            # Rankings of the teams
            team_a_rank = match['team_related_match'][0]['rank']
            team_b_rank = match['team_related_match'][1]['rank']

            # Calculate points and classify groups
            a_points = self.calculate_points(team_a_last_5_games)
            b_points = self.calculate_points(team_b_last_5_games)
            a_recent_group = self.classify_a_points(a_points)
            b_recent_group = self.classify_b_points(b_points)
            rank_diff = self.calculate_rank_difference(team_a_rank, team_b_rank)

            # Classify teams based on odds
            a_team = self.classify_a_team(a_odds)
            b_team = self.classify_b_team(b_odds)
            
            # Generate the prediction result based on the data
            prediction_result, row_number = self.generate_result(a_team, b_team, a_recent_group, b_recent_group, rank_diff)

            # Generate match result and card using OpenAI, and capture the prompt used
            prompt_text, card_choice = self.generate_match_result_with_openai(
                a_team_name, b_team_name, home_team_name, away_team_name, prediction_result
            )



            processor = MatchDataProcessor(prompt_text)
            word_count = processor.calculate_word_count()
            reading_time = processor.calculate_reading_time()

            game_data_json = {
                "description": prompt_text,
                "word_count": word_count,
                "reading_time": reading_time,
                "team_home": home_team_name,
                "team_away": away_team_name,
                "card": card_choice,
                "row_number" : row_number,
                "rank_diff" : rank_diff,
                "a_team" : a_team,
                "b_team" : b_team,
                "a_points" : a_points,
                "b_points" : b_points,
                "a_recent_group" : a_recent_group,
                "b_recent_group" : b_recent_group
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


            output_path = os.path.join(self.output_folder, f"match_{i+1}.json")
            with open(output_path, 'w') as file:
                json.dump(game_data_json, file, indent=4)

            print(f"Saved results for match {match_id} in {output_path}")
            print("=" * 50)

        print("All games processed successfully.")
        return match_data_list


    def generate_match_result_with_openai(self,a_team_name, b_team_name, home_team_name, away_team_name, prediction_result):
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
    def calculate_points_summary(self,last_5_games):
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
    def calculate_points(self,last_5_games):
        if not isinstance(last_5_games, list):
            logging.error("Invalid input: last_5_games should be a list")
            return 0  # Return 0 points if the input is invalid

        points = 0

        for game in last_5_games:
            if game == 'w':  # Win
                points += 3
            elif game == 'd':  # Draw
                points += 1
            elif game == 'l':
                points +=0 
            else :
                logging.warning(f"Unexpected game result: {game}, ignoring it.")
        logging.info(f"Total points calculated: {points}")
        return points

    def classify_a_points(self,a_points):
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


    def classify_b_points(self,b_points):
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


    def calculate_rank_difference(self,rank_a, rank_b):
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
            classification = self.RankDifference.bigDifference
        elif 4 <= rank_diff <= 7:
            classification = self.RankDifference.mediumDifference
        else:
            classification = self.RankDifference.smallDifference

        # Log the classification result
        logging.info(f"Rank difference between rank_a={rank_a} and rank_b={rank_b} is classified as: {classification}")
        return classification

    def classify_a_team(self,a_odds):
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


    def classify_b_team(self,b_odds):
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


    def generate_result(self,a_team, b_team, a_recent_g, b_recent_g, rank_diff):

        # Rows 1-17 (A2 as A team)
        if a_team == "A1":
            return "A win", 1
        # Rows for A2
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
        elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "bigDifference":
            return "A win", 18
        elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "mediumDifference":
            return "A win", 19
        elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "smallDifference":
            return "A win or draw", 20
        elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5" :
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
            return "A win or draw", 26  
        elif a_team == "A4":
            return "A win or draw", 27
        elif a_team == "A5" and b_team == "B7" and a_recent_g == "ARecentG1":
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
        elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference":
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
            return "A or B win", 51
        elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG6":
            return "A win or draw", 52
        elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG7":
            return "A or B win", 53
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
            return "A win or draw", 54
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
            return "A win or draw", 55
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
            return "A win or draw", 56
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4":
            return "A win or draw", 57
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference":
            return "A win or draw", 58
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
            return "A or B win", 59
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
            return "A or B win", 60
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
            return "A win or draw", 61
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
            return "A or B win", 62
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
            return "A or B win", 63
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG1" :
            return "A or B win", 64
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG7" :
            return "A win or draw", 65
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG6" :
            return "A win or draw", 66
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG5" :
            return "A win or draw", 67
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
            return "A win or draw", 68
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
            return "A or B win", 69
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
            return "A or B win", 70
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG3":
            return "A or B win", 71
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2":
            return "A or B win", 72
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1":
            return "A or B win", 73
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG7" :
            return "A win or draw", 74
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG6" :
            return "A win or draw", 75
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "bigDifference":
            return "A win or draw", 76
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "mediumDifference":
            return "A or B win", 77
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "smallDifference":
            return "A or B win", 78
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG4":
            return "A or B win", 79
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG3":
            return "A or B win", 80
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG2" :
            return "A or B win", 81
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG1" :
            return "A or B win", 82
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7" :
            return "A win or draw", 83
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "bigDifference":
            return "A win or draw", 84
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "mediumDifference":
            return "A or B win", 85
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "smallDifference":
            return "A or B win", 86
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5":
            return "A or B win", 87
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" :
            return "A or B win", 88
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG3" :
            return "A or B win", 89
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG2":
            return "A or B win", 90
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG1":
            return "A or B win", 91
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG7":
            return "A or B win", 92
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG6":
            return "A or B win", 93
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG5":
            return "A or B win", 94
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG4":
            return "A or B win", 95
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG3":
            return "A or B win", 96
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
            return "A or B win", 97
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
            return "A or B win", 98
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
            return "B win or Draw", 99
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG1":
            return "B win or Draw", 100
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG7" :
            return "A or B win", 101
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG6":
            return "A or B win", 102
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG5":
            return "A or B win", 103
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG4":
            return "A or B win", 104
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG3":
            return "A or B win", 105
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
            return "A or B win", 106
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
            return "B win or draw", 107
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
            return "B win or draw", 108
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG1" :
            return "B win or draw", 109
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG7" :
            return "B win or draw", 110
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG6":
            return "A or B win", 111
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG5":
            return "A or B win", 112
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
            return "A or B win", 113
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
            return "B win or draw", 114
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
            return "B win or draw", 115
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG3" :
            return "B win or draw", 116
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG2" :
            return "B win or draw", 117
        elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG1" :
            return "B win or draw", 118
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
            return "A win or draw", 119
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
            return "A win or draw", 120
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
            return "A win or draw", 121
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
            return "A win or draw", 122
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
            return "A win or draw", 123
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
            return "A or B win", 124
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference" :
            return "A win or draw", 125
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
            return "A or B win", 126
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
            return "A or B win", 127
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" :
            return "A or B win", 128
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG1" :
            return "A or B win", 129
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1" :
            return "A or B win", 130
        elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2" :
            return "A or B win", 131
        elif a_team == "A7" and b_team == "B7"  :
            return "A win or draw", 132
        else :
            logging.warning(f"No result found for the combination: {a_team}, {b_team}, {a_recent_g}, {b_recent_g}, {rank_diff}")
            # Default condition if no match is found
            return "No result found", None

    def process(self):
        self.ensure_output_folder()
        # Fetch the match data
        self.fetch_odds_rank_and_last_5_games()
