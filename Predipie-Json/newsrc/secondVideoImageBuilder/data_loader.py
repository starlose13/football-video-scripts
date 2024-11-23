import json
import os

class DataLoader:
    def __init__(self, json_paths):
        base_dir = os.path.dirname(json_paths["match_introduction"])
        if not os.path.exists(base_dir):
            print(f"Error: JSON base directory '{base_dir}' does not exist.")
        else:
            for key, path in json_paths.items():
                if not os.path.exists(path):
                    print(f"Error: JSON file '{key}' not found at path: {path}")
        
        self.team_info_data = self.load_json_data(json_paths["match_introduction"])
        self.match_times_data = self.load_json_data(json_paths["stats"])
        self.odds_data = self.load_json_data(json_paths["odds"])
        self.recent_matches_data = self.load_json_data(json_paths["recent_matches"])
        self.card_results_data = self.load_json_data(json_paths["card_results"])

    @staticmethod
    def load_json_data(filepath):
        try:
            print(f"Loading JSON data from: {filepath}")
            with open(filepath, 'r') as file:
                data = json.load(file)
                print(f"Loaded data from {filepath}: {data[:2]}...")  
                return data
        except FileNotFoundError:
            print(f"Warning: JSON file not found at {filepath}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON file at {filepath}")
            return []

    def get_game_data(self, game_id):
        data = {}

        team_info = next((item for item in self.team_info_data if item.get("id") == game_id), None)
        if team_info:
            data['match_introduction'] = team_info
        else:
            print(f"Warning: No team info found for game_id {game_id}")

        match_time = next((item for item in self.match_times_data if item.get("id") == game_id), None)
        if match_time:
            data['stats'] = match_time
        else:
            print(f"Warning: No match time found for game_id {game_id}")

        odds = next((item for item in self.odds_data if item.get("id") == game_id), None)
        if odds:
            data['odds'] = odds
        else:
            print(f"Warning: No odds found for game_id {game_id}")

        recent_matches = next((item for item in self.recent_matches_data if item.get("id") == game_id), None)
        if recent_matches:
            data['recent_matches'] = recent_matches
        else:
            print(f"Warning: No recent matches found for game_id {game_id}")

        card_result = next((item for item in self.card_results_data if item.get("id") == game_id), None)
        if card_result:
            data['card'] = card_result.get('Card', "")
        else:
            print(f"Warning: No card result found for game_id {game_id}")

        print(f"Final data for game_id {game_id}: {data}")
        return data