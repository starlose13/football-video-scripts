from dotenv import load_dotenv
import openai
from typing import Dict, Any
import json
import os
import openai
from fetch_last_five_matches import FetchLast5Matches
from fetch_match_stats import FetchMatchTime
from fetch_odds_ranks import FetchOdds
from fetch_team_info import FetchTeamInfo
from reading_time_consumer import MatchDataProcessor
from config import BASE_URL , START_AFTER
from typing import Dict, Any


load_dotenv()

class GeneratePrompts:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def prompt_for_last5matches(self, match_info: Dict[str, Any]) -> str:
        """
        Generate a prompt based on last 5 matches information.
        """
        prompt = f"Generate a summary of the last 5 matches. The results are: {match_info}"
        response = openai.ChatCompletion.create(
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
        return {"prompt": generated_script, "reading_time": reading_time}

    def prompt_for_match_stats(self, match_stats: Dict[str, Any]) -> str:
        """
        Generate a prompt based on match stats.
        """
        prompt = f"PLACEHOLDER PROMPT for match stats based on: {match_stats}"
        response = openai.ChatCompletion.create(
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
        return {"prompt": generated_script, "reading_time": reading_time}

    def prompt_for_odds(self, odds_info: Dict[str, Any]) -> str:
        """
        Generate a prompt based on match odds.
        """
        prompt = f"PLACEHOLDER PROMPT for match odds based on: {odds_info}"
        response = openai.ChatCompletion.create(
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
        return {"prompt": generated_script, "reading_time": reading_time}

    def prompt_for_team_info(self, team_info: Dict[str, Any]) -> str:
        """
        Generate a prompt based on team information.
        """
        prompt = f"PLACEHOLDER PROMPT for team info based on: {team_info}"
        response = openai.ChatCompletion.create(
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
        return {"prompt": generated_script, "reading_time": reading_time}
    

    def save_prompt_to_json(self, data, filename, folder="prompt_output_folder"):
        """Saves the given data to a JSON file inside a specified folder."""
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Data successfully saved to {filepath}")

# Example usage
if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_key = openai.api_key
    prompt_generator = GeneratePrompts(api_key=api_key)
    
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    fetch_match_stats = FetchMatchTime(base_url=BASE_URL)
    fetch_odds = FetchOdds(base_url=BASE_URL)
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    
    last5matches_data = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    match_stats_data = fetch_match_stats.get_match_times(start_after=START_AFTER)
    odds_data = fetch_odds.get_odds(start_after=START_AFTER)
    team_info_data = fetch_team_info.get_team_info(start_after=START_AFTER)

    # Generate prompts
    last5matches_result = prompt_generator.prompt_for_last5matches(last5matches_data)
    prompt_generator.save_prompt_to_json(last5matches_result, "last5matches_prompt.json")

    match_stats_result = prompt_generator.prompt_for_match_stats(match_stats_data)
    prompt_generator.save_prompt_to_json(match_stats_result, "match_stats_prompt.json")

    odds_result = prompt_generator.prompt_for_odds(odds_data)
    prompt_generator.save_prompt_to_json(odds_result, "odds_prompt.json")

    team_info_result = prompt_generator.prompt_for_team_info(team_info_data)
    prompt_generator.save_prompt_to_json(team_info_result, "team_info_prompt.json")

    

