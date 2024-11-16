import os
import openai
import json
from fetch_last_five_matches import FetchLast5Matches
from fetch_match_stats import FetchMatchTime
from fetch_odds_ranks import FetchOdds
from fetch_team_info import FetchTeamInfo
from generate_prompts import GeneratePrompts
from config import BASE_URL, START_AFTER

def save_to_json(data, filename):
    """Utility function to save data to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Saved data to {filename}")

def main_pipeline(api_key: str):
    # Initialize OpenAI API key
    openai.api_key = api_key

    # Step 1: Fetch Team Information
    print("Step 1: Fetching Team Information...")
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    team_info_data = fetch_team_info.get_team_info(start_after=START_AFTER)
    save_to_json(team_info_data, "team_info_data.json")

    # Step 2: Fetch Match Odds
    print("Step 2: Fetching Match Odds...")
    fetch_odds = FetchOdds(base_url=BASE_URL)
    odds_data = fetch_odds.get_odds(start_after=START_AFTER)
    save_to_json(odds_data, "odds_data.json")

    # Step 3: Fetch Match Stats
    print("Step 3: Fetching Match Stats...")
    fetch_match_stats = FetchMatchTime(base_url=BASE_URL)
    match_stats_data = fetch_match_stats.get_match_times(start_after=START_AFTER)
    save_to_json(match_stats_data, "match_stats_data.json")

    # Step 4: Fetch Last 5 Matches
    print("Step 4: Fetching Last 5 Matches...")
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    last5matches_data = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    save_to_json(last5matches_data, "last5matches_data.json")

    # Step 5: Generate Prompts and Save them with Reading Time
    print("Step 5: Generating Prompts and Calculating Reading Time...")
    prompt_generator = GeneratePrompts(api_key=api_key)

    # Generate and save prompt for team info
    team_info_prompt = prompt_generator.prompt_for_team_info(team_info_data)
    prompt_generator.save_prompt_to_json(team_info_prompt, "team_info_prompt.json")

    # Generate and save prompt for odds
    odds_prompt = prompt_generator.prompt_for_odds(odds_data)
    prompt_generator.save_prompt_to_json(odds_prompt, "odds_prompt.json")

    # Generate and save prompt for match stats
    match_stats_prompt = prompt_generator.prompt_for_match_stats(match_stats_data)
    prompt_generator.save_prompt_to_json(match_stats_prompt, "match_stats_prompt.json")

    # Generate and save prompt for last 5 matches
    last5matches_prompt = prompt_generator.prompt_for_last5matches(last5matches_data)
    prompt_generator.save_prompt_to_json(last5matches_prompt, "last5matches_prompt.json")

    print("Pipeline executed successfully. All prompts and data saved as JSON files.")

if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_key = openai.api_key
    main_pipeline(api_key=api_key)



