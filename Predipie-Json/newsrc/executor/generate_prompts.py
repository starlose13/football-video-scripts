from datetime import datetime
import time
from dotenv import load_dotenv
import openai
from typing import Dict, Any, List
import json
import os
from utils.json_saver import JsonSaver
from dataFetcher.fetch_last_five_matches import FetchLast5Matches
from dataFetcher.fetch_match_stats import FetchMatchTime
from dataFetcher.fetch_odds_ranks import FetchOddsRanks
from dataFetcher.fetch_team_info import FetchTeamInfo
from utils.reading_time_consumer import MatchDataProcessor
from config.config import BASE_URL, START_AFTER, START_BEFORE, PROGRAM_NAME
from dataClassifier.game_result_predictor import GameResultPredictor
from utils.program_counter import increment_program_number, get_program_number
from openai.error import RateLimitError
from finalScore.results_with_start_before import ScoreCalculator

load_dotenv()

class GeneratePrompts:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    def openai_request_with_retry(self, model, messages, max_tokens, retries=5):
        """Helper function to make an OpenAI request with retries and exponential backoff."""
        delay = 2  # Initial delay in seconds
        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response
            except RateLimitError:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        print("Max retries reached. Could not complete the request.")
        return None
    
    def extract_scores(self, score: str) -> Dict[str, int]:
        """Extract the home and away scores from the score string."""
        try:
            home_score, away_score = map(int, score.split("-"))
            return {"home_score": home_score, "away_score": away_score}
        except ValueError:
            print(f"Invalid score format: {score}")
            return {"home_score": 0, "away_score": 0}
        
    def parse_timestamp(self, timestamp: str) -> Dict[str, str]:
        """Parse the timestamp into date, day, and time."""
        match_datetime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = match_datetime.strftime("%Y-%m-%d")
        day_str = match_datetime.strftime("%A")
        time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
        return {"date": date_str, "day": day_str, "time": time_str}

    def load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from a file in the data folder."""
        filepath = os.path.join(self.data_folder, filename)
        with open(filepath, 'r') as file:
            return json.load(file)
   
#################################################################################################################
######################################FIRST VIDEO STARTED HERE###################################################
#################################################################################################################

    def generate_first_video_intro_with_openai(self) -> Dict[str, Any]:
        """Generates an introduction for the narration using OpenAI."""
        prompt = (
            f"Start with: 'Hi {PROGRAM_NAME}! ' Tonight, we’re bringing you 5 fantastic lineup of top matches for you. "
            f"Keep it upbeat, friendly, and super energetic. Make it concise—under 40 words with a punchy, engaging tone! "
            f"Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            f"Important: Do not mention any game statistics, player names, or game history information in the output."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating an introductory narration for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        generated_intro = response['choices'][0]['message']['content'].strip()
        processor = MatchDataProcessor(generated_intro)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_intro, "reading_time": reading_time}

    def generate_final_score_prompt(self, match_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on final scores for each match."""
        prompts = []

        for match in match_data:
            home_team = match.get("home_team_name", "N/A")
            away_team = match.get("away_team_name", "N/A")
            start_timestamp = match.get("startTimestamp", "N/A")
            score = match.get("Score", "N/A")

            # Parse timestamp and scores
            parsed_timestamp = self.parse_timestamp(start_timestamp)
            extracted_scores = self.extract_scores(score)

            if extracted_scores['home_score'] > extracted_scores['away_score']:
                result_sentence = f"{home_team} won the match with a score of {extracted_scores['home_score']}-{extracted_scores['away_score']} against {away_team}."
            elif extracted_scores['home_score'] < extracted_scores['away_score']:
                result_sentence = f"{away_team} won the match with a score of {extracted_scores['away_score']}-{extracted_scores['home_score']} against {home_team}."
            else:
                result_sentence = f"The match ended in a draw with a score of {extracted_scores['home_score']}-{extracted_scores['away_score']} between {home_team} and {away_team}."

            prompt = (
            f"The match between {home_team} and {away_team} was held on {parsed_timestamp['day']} at {parsed_timestamp['time']}."
            f"{result_sentence}"
            )

            # Append prompt
            prompts.append({"match_id": match.get("id", "N/A"), "prompt": prompt})

        return prompts

    def save_prompts(self, prompts: List[Dict[str, Any]], filename: str, custom_folder: str):
        """Save generated prompts to a JSON file."""
        output_path = os.path.join(custom_folder, filename)
        os.makedirs(custom_folder, exist_ok=True)
        with open(output_path, 'w', encoding="utf-8") as file:
            json.dump(prompts, file, ensure_ascii=False, indent=4)
        print(f"Prompts saved to {output_path}")
        
    def generate_first_video_closing_with_openai(self) -> Dict[str, Any]:
        """Generates an introduction for the narration using OpenAI."""
        prompt = (
            f"Start with: 'Hi {PROGRAM_NAME}! ' Tonight, we’re bringing you 5 fantastic lineup of top matches for you. "
            f"Keep it upbeat, friendly, and super energetic. Make it concise—under 40 words with a punchy, engaging tone! "
            f"Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            f"Important: Do not mention any game statistics, player names, or game history information in the output."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating an introductory narration for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        generated_intro = response['choices'][0]['message']['content'].strip()
        processor = MatchDataProcessor(generated_intro)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_intro, "reading_time": reading_time}

#################################################################################################################
######################################FIRST VIDEO ENDED HERE#####################################################
#################################################################################################################

                                                #####

#################################################################################################################
######################################SECOND VIDEO STARTED HERE##################################################
#################################################################################################################

    def generate_second_video_intro_with_openai(self) -> Dict[str, Any]:
        """Generates an introduction for the narration using OpenAI."""
        prompt = (
            f"Start with: 'Hi {PROGRAM_NAME}! ' Tonight, we are bringing you 5 fantastic lineup of top matches for you. "
            f"Keep it upbeat, friendly, and super energetic. Make it concise—under 40 words with a punchy, engaging tone! "
            f"Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            f"Important: Do not mention any game statistics, player names, or game history information in the output."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating an introductory narration for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        generated_intro = response['choices'][0]['message']['content'].strip()
        processor = MatchDataProcessor(generated_intro)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_intro, "reading_time": reading_time}
    
    def prompt_for_team_info(self, team_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on team information for each game with a dynamic introductory phrase."""
        prompts = []
        for i, team_info in enumerate(team_data, start=1):
            home_team_name = team_info.get("home_team_name", "Unknown Home Team")
            away_team_name = team_info.get("away_team_name", "Unknown Away Team")

            if i == 1:
                intro = f"Let's start with the first match: {home_team_name} versus {away_team_name}."
            elif i in [2, 3, 4]:
                ordinal = {2: "second", 3: "third", 4: "fourth"}[i]
                intro = f"Let's continue with the {ordinal} match: {home_team_name} against {away_team_name}."
            else:  
                intro = f"And the last match: {home_team_name} versus {away_team_name}."

            prompt = (
                f"{intro} Create a brief, dynamic match description under 80 characters, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                f"Important: Do not mention any game statistics, player names, or game history information."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating dynamic descriptions based on team info."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            
            prompts.append({
                "prompt": generated_script,
                "home_team_name": home_team_name,
                "away_team_name": away_team_name,
                "reading_time": reading_time
            })
            
        return prompts
    
    def prompt_for_match_stats(self, match_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on match stats for each game with specific match details."""
        prompts = []
        for stats in match_stats:
            # Extract match details
            home_team = stats.get("home_team", "Unknown Home Team")
            away_team = stats.get("away_team", "Unknown Away Team")
            match_time = stats.get("time", "Unknown Time")
            start_timestamp = stats.get("startTimestamp", "")
            
            # Format the match time
            if start_timestamp:
                match_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
                time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
                day_str = match_datetime.strftime("%A")
                date_str = match_datetime.strftime("%Y-%m-%d")
            else:
                time_str = "Unknown Time"
                day_str = "Unknown Day"
                date_str = "Unknown Date"

            # Construct the prompt with the chosen format
            prompt = (
                f"As if you're a live TV host, build excitement for the game of football between {home_team} and {away_team}. "
                f"This match starts at: {time_str} on {day_str}, {date_str}. "
                "Keep it upbeat, clear, and full of energy to captivate the audience. "
                "Also, make it concise and under 22 words. "
                "Remember: only use these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
            )

            # Generate response from OpenAI
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            # Store the generated prompt and reading time
            prompts.append({
                "prompt": generated_script,
                "home_team": home_team,
                "away_team": away_team,
                "date": date_str,
                "day": day_str,
                "time": time_str,
                "reading_time": reading_time
            })
            
        return prompts

    def prompt_for_odds(self, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on odds information for each game."""
        prompts = []
        for odds in odds_data:
            # Extract relevant details
            home_team = odds.get("home_team", "Unknown Home Team")
            away_team = odds.get("away_team", "Unknown Away Team")
            
            # Extract odds information if available
            if odds.get("odds"):
                home_odds = odds["odds"][0].get("homeWin", "N/A")
                draw_odds = odds["odds"][0].get("draw", "N/A")
                away_odds = odds["odds"][0].get("awayWin", "N/A")
            else:
                home_odds = "N/A"
                draw_odds = "N/A"
                away_odds = "N/A"
            
            # Construct the prompt similar to the required output
            prompt = (
                f"[Generate a concise and complete description for football match odds, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                f"Provide only the odds information directly, without introducing the teams or match. State each type of odds clearly and avoid abbreviations or parentheses. Keep it under 45 words.] "
                f"The home team, {home_team}, has odds of winning at {home_odds}. The away team, {away_team}, has odds of winning at {away_odds}. The odds for a draw are {draw_odds}."
            )

            # Generate response from OpenAI
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with odds information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            # Store the generated prompt and reading time
            prompts.append({
                "prompt": generated_script,
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
                "reading_time": reading_time
            })
            
        return prompts


    def prompt_for_last5matches(self, matches_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on the last 5 matches for each game."""
        prompts = []
        for match_info in matches_data:
            home_team = match_info["home_team"]["team_name"]
            guest_team = match_info["away_team"]["team_name"]
            home_results = match_info["home_team"]["last_5_matches"]
            guest_results = match_info["away_team"]["last_5_matches"]

            home_wins = match_info["home_team"]["results_count"]["wins"]
            home_draws = match_info["home_team"]["results_count"]["draws"]
            home_losses = match_info["home_team"]["results_count"]["losses"]

            guest_wins = match_info["away_team"]["results_count"]["wins"]
            guest_draws = match_info["away_team"]["results_count"]["draws"]
            guest_losses = match_info["away_team"]["results_count"]["losses"]

            prompt = (
                f"[Generate a concise description of each team’s recent form, using full words for clarity and avoiding abbreviations like 'W', 'D', or 'L'. "
                f"Focus on readability. Limit to 200 characters. Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon.] "
                f"The {home_team} recent form shows {home_results} (Wins: {home_wins}, Draws: {home_draws}, Losses: {home_losses}), "
                f"while the {guest_team} has recorded {guest_results} (Wins: {guest_wins}, Draws: {guest_draws}, Losses: {guest_losses})."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with recent form information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts


    def prompt_for_match_result(self, match_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on predicted match results for each game."""
        prompts = []
        for result in match_results:
            # اطلاعات تیم میزبان، تیم مهمان، و Card
            home_team_name = result["home_team_name"]
            away_team_name = result["away_team_name"]
            card = result["Card"]

            # ساخت شرط‌ها برای پرامپت
            if card == "Win Home Team":
                condition_text = f"My analysis predicts the {home_team_name} will win this match."
            elif card == "Win Away Team":
                condition_text = f"My analysis predicts the {away_team_name} will win this match."
            elif card == "Win or Draw Home Team":
                condition_text = f"The prediction suggests that the {home_team_name} will win or at least secure a draw."
            elif card == "Win or Draw Away Team":
                condition_text = f"The prediction suggests that the {away_team_name} will win or at least secure a draw."
            elif card == "Win Home or Away Team":
                condition_text = f"The prediction suggests that either the {home_team_name} or the {away_team_name} will claim victory."
            else:
                condition_text = "No specific prediction is available for this match."

            prompt = (
                f"{condition_text} Keep it concise and engaging—under 25 words! "
                "Use these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                "Avoid mentioning betting or related terminology."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating dynamic and engaging football match result predictions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )

            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({"prompt": generated_script, "card": card, "reading_time": reading_time})

        return prompts


    def generate_second_video_closing_with_openai(self, program_number: int) -> Dict[str, Any]:
        """Generates a closing statement for the narration using OpenAI."""
        prompt = (
            f"Wrap up Episode {program_number} with a friendly closing: 'Just a reminder, I'm only an AI, this isn’t financial advice!' "
            f"Encourage viewers to tune in daily, join the {PROGRAM_NAME} community, and get ready for Episode {program_number + 1} tomorrow. "
            f"End with: 'don't trade your life for entertainment! Goodbye!' "
            f"Keep it complete and under 40 words. Use these punctuation marks frequently: dot, comma, exclamation mark, question mark, and semicolon. Don't use dash or underscore."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating a friendly closing statement for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        generated_closing = response['choices'][0]['message']['content'].strip()
        processor = MatchDataProcessor(generated_closing)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_closing, "reading_time": reading_time}
    
#################################################################################################################
######################################SECOND VIDEO ENDED HERE####################################################
#################################################################################################################

    def generate_second_video_narration(
        self,
        intro_result: Dict[str, Any],
        team_info_result: List[Dict[str, Any]],
        match_stats_result: List[Dict[str, Any]],
        odds_result: List[Dict[str, Any]],
        last5matches_result: List[Dict[str, Any]],
        match_result_prompts: List[Dict[str, Any]],
        closing_result: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generates a combined narration for the second video in a single field."""

        narration_text = intro_result["prompt"] + "\n\n"

        # Append data for each game
        for i in range(5):
            narration_text += (
                team_info_result[i]["prompt"] +
                match_stats_result[i]["prompt"] +
                odds_result[i]["prompt"] +
                last5matches_result[i]["prompt"] + 
                match_result_prompts[i]["prompt"]
            )

        # Append the closing section
        narration_text += closing_result["prompt"]

        # Return a single dictionary with the combined narration
        return {"narration": narration_text}
    
if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_key = openai.api_key
    prompt_generator = GeneratePrompts(api_key=api_key)
    json_saver = JsonSaver()
    today_date = START_AFTER
    yesterday_date = START_BEFORE
    # Increase program number
    increment_program_number()
    program_number = get_program_number()
    
    # Fetch data
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    fetch_match_stats = FetchMatchTime(base_url=BASE_URL)
    fetch_odds = FetchOddsRanks(base_url=BASE_URL)
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    game_result_predictor = GameResultPredictor()
    fetch_final_score = ScoreCalculator(base_url=BASE_URL,start_after=START_BEFORE)
    
    game_results = game_result_predictor.predict_game_results()

    ##################################### GENERATE PROMPTS OF FIRST VIDEO  #####################################
    ############################################################################################################
    fetch_final_score.update_scores_in_file()
    final_score_prompt_output_folder_name = "first_video"
    output_folder = os.path.join(START_BEFORE + "_json_match_output_folder", "final_score_prompt_output_folder_name")
    final_score_data_path = os.path.join(yesterday_date + "_json_match_output_folder", "match_prediction_result.json")
    if os.path.exists(final_score_data_path):
        with open(final_score_data_path, 'r', encoding="utf-8") as file:
            final_score_data = json.load(file)
    else:
        print(f"Error: File {final_score_data_path} not found.")
        final_score_data = []
    final_score_prompts = prompt_generator.generate_final_score_prompt(final_score_data)
    json_saver.save_to_json(final_score_prompts, "final_score_prompt.json",custom_folder=output_folder)
    
    ##################################### GENERATE PROMPTS OF SECOND VIDEO  #####################################
    #############################################################################################################
    last5matches_data = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    match_stats_data = fetch_match_stats.get_match_times(start_after=START_AFTER)
    odds_data = fetch_odds.get_odds_ranks(start_after=START_AFTER)
    team_info_data = fetch_team_info.get_team_info(start_after=START_AFTER)

    narration_folder = os.path.join(today_date + "_json_match_output_folder", "narrations")
    prompt_folder = os.path.join(today_date + "_json_match_output_folder", "prompts")

    intro_result = prompt_generator.generate_second_video_intro_with_openai()
    json_saver.save_to_json(intro_result, "intro_prompt.json",custom_folder=prompt_folder)

    closing_result = prompt_generator.generate_second_video_closing_with_openai(program_number=program_number)
    json_saver.save_to_json(closing_result, "closing_prompt.json",custom_folder=prompt_folder)

    last5matches_result = prompt_generator.prompt_for_last5matches(last5matches_data)
    json_saver.save_to_json(last5matches_result, "last5matches_prompt.json",custom_folder=prompt_folder)

    match_stats_result = prompt_generator.prompt_for_match_stats(match_stats_data)
    json_saver.save_to_json(match_stats_result, "match_stats_prompt.json",custom_folder=prompt_folder)

    odds_result = prompt_generator.prompt_for_odds(odds_data)
    json_saver.save_to_json(odds_result, "odds_prompt.json",custom_folder=prompt_folder)

    team_info_result = prompt_generator.prompt_for_team_info(team_info_data)
    json_saver.save_to_json(team_info_result, "team_info_prompt.json",custom_folder=prompt_folder)

    match_result_prompt = prompt_generator.prompt_for_match_result(game_results)
    json_saver.save_to_json(match_result_prompt, "match_result_prompt.json",custom_folder=prompt_folder)

    second_video_result = prompt_generator.generate_second_video_narration(
        intro_result=intro_result,
        team_info_result=team_info_result,
        match_stats_result=match_stats_result,
        odds_result=odds_result,
        last5matches_result=last5matches_result,
        match_result_prompts =match_result_prompt,
        closing_result=closing_result
    )
    json_saver.save_to_json(second_video_result, "second_video_narration.json", custom_folder=narration_folder)
