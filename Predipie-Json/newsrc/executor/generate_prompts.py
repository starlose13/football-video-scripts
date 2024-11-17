import time
from dotenv import load_dotenv
import openai
from typing import Dict, Any, List
import json
import os
from dataFetcher.fetch_last_five_matches import FetchLast5Matches
from dataFetcher.fetch_match_stats import FetchMatchTime
from dataFetcher.fetch_odds_ranks import FetchOddsRanks
from dataFetcher.fetch_team_info import FetchTeamInfo
from utils.reading_time_consumer import MatchDataProcessor
from config.config import BASE_URL, START_AFTER, START_BEFORE, PROGRAM_NAME
from dataClassifier.game_result_predictor import GameResultPredictor
from utils.program_counter import increment_program_number, get_program_number
from openai.error import RateLimitError

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

    def load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from a file in the data folder."""
        filepath = os.path.join(self.data_folder, filename)
        with open(filepath, 'r') as file:
            return json.load(file)

    def generate_intro_with_openai(self) -> Dict[str, Any]:
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
    

    def generate_closing_with_openai(self, program_number: int) -> Dict[str, Any]:
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

    def prompt_for_last5matches(self, matches_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on the last 5 matches for each game."""
        prompts = []
        for match_info in matches_data:
            prompt = f"Generate a summary of the last 5 matches. The results are: {match_info}"
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating dynamic descriptions based on recent form."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts
    
    def prompt_for_match_stats(self, match_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on match stats for each game."""
        prompts = []
        for stats in match_stats:
            prompt = f"PLACEHOLDER PROMPT for match stats based on: {stats}"
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating dynamic descriptions based on match stats."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts

    def prompt_for_odds(self, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on odds for each game."""
        prompts = []
        for odds in odds_data:
            prompt = f"PLACEHOLDER PROMPT for match odds based on: {odds}"
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating dynamic descriptions based on match odds."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts

    def prompt_for_team_info(self, team_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on team information for each game."""
        prompts = []
        for team_info in team_data:
            prompt = f"PLACEHOLDER PROMPT for team info based on: {team_info}"
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
            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts

    def prompt_for_match_result(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prompts based on predicted match results for each game."""
        prompts = []
        for prediction in predictions:
            a_team_name = prediction["Team A"]
            b_team_name = prediction["Team B"]
            prediction_result = prediction["Result"]

            if prediction_result == "A win or draw":
                condition_text = f"My AI analysis suggests {a_team_name} will win or draw."
                card = "Win or Draw Home Team" if a_team_name == prediction["Team A"] else "Win or Draw Away Team"
            elif prediction_result == "A or B win":
                condition_text = f"My AI analysis suggests either {a_team_name} or {b_team_name} will win."
                card = "Win Home or Away Team"
            elif prediction_result == "A win":
                condition_text = f"My AI analysis suggests {a_team_name} will win."
                card = "Win Home Team" if a_team_name == prediction["Team A"] else "Win Away Team"
            else:
                condition_text = "No specific result is found for this prediction."
                card = "none"

            prompt = (
                f"{condition_text} Write this dynamically for football fans, keeping it very brief—under 25 words! "
                "Use punctuation marks like dot, comma, exclamation mark, question mark, and semicolon. "
                "Avoid words like 'bet,' 'betting,' or 'place bet.'"
            )
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating football match result summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            prompts.append({"prompt": generated_script, "card": card, "reading_time": reading_time})
            
        return prompts
    

    def generate_final_score_prompt(self) -> Dict[str, Any]:
        """Reads final score from the folder with START_BEFORE and generates a prompt with it."""
        
        # Set the output folder path based on START_BEFORE date
        output_folder = f"{START_BEFORE}_output"
        final_score_path = os.path.join(output_folder, "final_scores.json")
        
        if os.path.exists(final_score_path):
            with open(final_score_path, 'r') as file:
                final_score_data = json.load(file)
                
                # Check if final_score_data is a list and get the first item if so
                if isinstance(final_score_data, list) and final_score_data:
                    final_score = final_score_data[0].get("finalScore", "unknown")
                elif isinstance(final_score_data, dict):
                    final_score = final_score_data.get("finalScore", "unknown")
                else:
                    final_score = "unknown"
            
            prompt = f"The result of the game was {final_score}. Generate a brief commentary for this score."
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating commentary based on the final score of a football match."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            
            return {"prompt": generated_script, "reading_time": reading_time}
        else:
            print(f"No final score file found at {final_score_path}")
            return {"prompt": "No final score available", "reading_time": 0}
        


    def generate_first_video_narration(
        self,
        intro_result: Dict[str, Any],
        team_info_result: List[Dict[str, Any]],
        match_stats_result: List[Dict[str, Any]],
        odds_result: List[Dict[str, Any]],
        last5matches_result: List[Dict[str, Any]],
        match_result_prompts: List[Dict[str, Any]],
        closing_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generates combined narrations for the first video for each game using individual prompt results."""

        narrations = []
        
        # Combine all parts of the narration for each game
        for i in range(len(team_info_result)):
            narration_text = (
                intro_result["prompt"] + "\n" +
                team_info_result[i]["prompt"] + "\n" +
                match_stats_result[i]["prompt"] + "\n" +
                odds_result[i]["prompt"] + "\n" +
                last5matches_result[i]["prompt"] + "\n" +
                match_result_prompts[i]["prompt"] + "\n" +
                closing_result["prompt"]
            )

            # Prepare the final output with all individual prompts and combined narration for each game
            narration_dict = {
                "intro": intro_result["prompt"],
                "team_info": team_info_result[i]["prompt"],
                "match_stats": match_stats_result[i]["prompt"],
                "odds": odds_result[i]["prompt"],
                "last5matches": last5matches_result[i]["prompt"],
                "match_result": match_result_prompts[i]["prompt"],
                "closing": closing_result["prompt"],
                "narration": narration_text
            }
            
            narrations.append(narration_dict)
        
        return narrations


    
    def save_prompt_to_json(self, data, filename, folder="prompt_output_folder"):
        """Saves the given data to a JSON file inside a specified folder."""
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Data successfully saved to {filepath}")

if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_key = openai.api_key
    prompt_generator = GeneratePrompts(api_key=api_key)
    
    # Increase program number
    increment_program_number()
    program_number = get_program_number()
    
    # Fetch data
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    fetch_match_stats = FetchMatchTime(base_url=BASE_URL)
    fetch_odds = FetchOddsRanks(base_url=BASE_URL)
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    
    last5matches_data = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    match_stats_data = fetch_match_stats.get_match_times(start_after=START_AFTER)
    odds_data = fetch_odds.get_odds_ranks(start_after=START_AFTER)
    team_info_data = fetch_team_info.get_team_info(start_after=START_AFTER)
    
    game_result_predictor = GameResultPredictor()
    game_results = game_result_predictor.predict_game_results()

    # Generate prompts
    intro_result = prompt_generator.generate_intro_with_openai()
    prompt_generator.save_prompt_to_json(intro_result, "intro_prompt.json")

    closing_result = prompt_generator.generate_closing_with_openai(program_number=program_number)
    prompt_generator.save_prompt_to_json(closing_result, "closing_prompt.json")

    final_score_prompt = prompt_generator.generate_final_score_prompt()
    prompt_generator.save_prompt_to_json(final_score_prompt, "final_score_prompt.json")

    last5matches_result = prompt_generator.prompt_for_last5matches(last5matches_data)
    prompt_generator.save_prompt_to_json(last5matches_result, "last5matches_prompt.json")

    match_stats_result = prompt_generator.prompt_for_match_stats(match_stats_data)
    prompt_generator.save_prompt_to_json(match_stats_result, "match_stats_prompt.json")

    odds_result = prompt_generator.prompt_for_odds(odds_data)
    prompt_generator.save_prompt_to_json(odds_result, "odds_prompt.json")

    team_info_result = prompt_generator.prompt_for_team_info(team_info_data)
    prompt_generator.save_prompt_to_json(team_info_result, "team_info_prompt.json")

    # Check if there are game results before generating the match result prompt
    match_result_prompt = prompt_generator.prompt_for_match_result(game_results)
    prompt_generator.save_prompt_to_json(match_result_prompt, "match_result_prompt.json")

    # Generate the first video narration by passing the previously generated results
    first_video_result = prompt_generator.generate_first_video_narration(
        intro_result=intro_result,
        team_info_result=team_info_result,
        match_stats_result=match_stats_result,
        odds_result=odds_result,
        last5matches_result=last5matches_result,
        match_result_prompts =match_result_prompt,
        closing_result=closing_result
    )
    prompt_generator.save_prompt_to_json(first_video_result, "first_video_prompt.json")
